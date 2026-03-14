from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from decimal import Decimal
import uuid

from .models import User, Account, Transaction, Card, Loan, Beneficiary, Notification
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ChangePasswordSerializer,
    AccountSerializer, TransactionSerializer, DepositSerializer,
    WithdrawalSerializer, TransferSerializer, CardSerializer,
    LoanSerializer, LoanApplicationSerializer, BeneficiarySerializer,
    NotificationSerializer
)


# ─── Auth Views ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Logged out successfully'})


@api_view(['GET', 'PUT', 'PATCH'])
def profile(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Dashboard ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def dashboard(request):
    user = request.user
    accounts = Account.objects.filter(user=user, status='ACTIVE')
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    account_ids = accounts.values_list('id', flat=True)
    recent_transactions = Transaction.objects.filter(
        Q(from_account__in=account_ids) | Q(to_account__in=account_ids)
    ).order_by('-created_at')[:10]
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    active_cards = Card.objects.filter(account__in=accounts, status='ACTIVE').count()
    active_loans = Loan.objects.filter(user=user, status='ACTIVE').count()

    return Response({
        'total_balance': str(total_balance),
        'accounts': AccountSerializer(accounts, many=True).data,
        'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
        'unread_notifications': unread_notifications,
        'active_cards': active_cards,
        'active_loans': active_loans,
    })


# ─── Account Views ───────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def accounts_list(request):
    if request.method == 'GET':
        accounts = Account.objects.filter(user=request.user)
        return Response(AccountSerializer(accounts, many=True).data)
    # Create new account
    data = request.data.copy()
    account = Account.objects.create(
        user=request.user,
        account_type=data.get('account_type', 'SAVINGS'),
        currency=data.get('currency', 'USD'),
        balance=0,
        available_balance=0
    )
    return Response(AccountSerializer(account).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
def account_detail(request, pk):
    try:
        account = Account.objects.get(id=pk, user=request.user)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(AccountSerializer(account).data)
    serializer = AccountSerializer(account, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Transaction Views ───────────────────────────────────────────────────────

@api_view(['GET'])
def transactions_list(request):
    user = request.user
    account_ids = Account.objects.filter(user=user).values_list('id', flat=True)
    transactions = Transaction.objects.filter(
        Q(from_account__in=account_ids) | Q(to_account__in=account_ids)
    )
    # Filters
    tx_type = request.query_params.get('type')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    account_id = request.query_params.get('account_id')

    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
    if account_id:
        transactions = transactions.filter(
            Q(from_account__id=account_id) | Q(to_account__id=account_id)
        )

    return Response(TransactionSerializer(transactions[:50], many=True).data)


@api_view(['GET'])
def transaction_detail(request, pk):
    try:
        account_ids = Account.objects.filter(user=request.user).values_list('id', flat=True)
        txn = Transaction.objects.get(
            Q(id=pk),
            Q(from_account__in=account_ids) | Q(to_account__in=account_ids)
        )
        return Response(TransactionSerializer(txn).data)
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def deposit(request):
    serializer = DepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        account = Account.objects.get(id=data['account_id'], user=request.user, status='ACTIVE')
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    with db_transaction.atomic():
        balance_before = account.balance
        account.balance += data['amount']
        account.available_balance += data['amount']
        account.save()
        txn = Transaction.objects.create(
            to_account=account,
            transaction_type='DEPOSIT',
            amount=data['amount'],
            currency=account.currency,
            status='COMPLETED',
            description=data.get('description', 'Deposit'),
            balance_before=balance_before,
            balance_after=account.balance,
            completed_at=timezone.now()
        )
        Notification.objects.create(
            user=request.user,
            title='Deposit Successful',
            message=f'${data["amount"]} deposited to account {account.account_number}',
            notification_type='TRANSACTION'
        )
    return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def withdraw(request):
    serializer = WithdrawalSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        account = Account.objects.get(id=data['account_id'], user=request.user, status='ACTIVE')
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    if account.available_balance < data['amount']:
        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        balance_before = account.balance
        account.balance -= data['amount']
        account.available_balance -= data['amount']
        account.save()
        txn = Transaction.objects.create(
            from_account=account,
            transaction_type='WITHDRAWAL',
            amount=data['amount'],
            currency=account.currency,
            status='COMPLETED',
            description=data.get('description', 'Withdrawal'),
            balance_before=balance_before,
            balance_after=account.balance,
            completed_at=timezone.now()
        )
        Notification.objects.create(
            user=request.user,
            title='Withdrawal Successful',
            message=f'${data["amount"]} withdrawn from account {account.account_number}',
            notification_type='TRANSACTION'
        )
    return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def transfer(request):
    serializer = TransferSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        from_account = Account.objects.get(id=data['from_account_id'], user=request.user, status='ACTIVE')
    except Account.DoesNotExist:
        return Response({'error': 'Source account not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        to_account = Account.objects.get(account_number=data['to_account_number'], status='ACTIVE')
    except Account.DoesNotExist:
        return Response({'error': 'Destination account not found'}, status=status.HTTP_404_NOT_FOUND)

    if from_account.id == to_account.id:
        return Response({'error': 'Cannot transfer to same account'}, status=status.HTTP_400_BAD_REQUEST)
    if from_account.available_balance < data['amount']:
        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

    fee = round(data['amount'] * Decimal('0.001'), 2)  # 0.1% fee
    total_deduct = data['amount'] + fee

    with db_transaction.atomic():
        from_balance_before = from_account.balance
        from_account.balance -= total_deduct
        from_account.available_balance -= total_deduct
        from_account.save()

        to_balance_before = to_account.balance
        to_account.balance += data['amount']
        to_account.available_balance += data['amount']
        to_account.save()

        txn = Transaction.objects.create(
            from_account=from_account,
            to_account=to_account,
            transaction_type='TRANSFER',
            amount=data['amount'],
            fee=fee,
            currency=from_account.currency,
            status='COMPLETED',
            description=data.get('description', 'Transfer'),
            balance_before=from_balance_before,
            balance_after=from_account.balance,
            completed_at=timezone.now()
        )
        Notification.objects.create(
            user=request.user,
            title='Transfer Successful',
            message=f'${data["amount"]} transferred to {to_account.account_number}',
            notification_type='TRANSACTION'
        )
    return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


# ─── Card Views ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def cards_list(request):
    account_ids = Account.objects.filter(user=request.user).values_list('id', flat=True)
    cards = Card.objects.filter(account__in=account_ids)
    return Response(CardSerializer(cards, many=True).data)


@api_view(['GET', 'PUT'])
def card_detail(request, pk):
    try:
        account_ids = Account.objects.filter(user=request.user).values_list('id', flat=True)
        card = Card.objects.get(id=pk, account__in=account_ids)
    except Card.DoesNotExist:
        return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(CardSerializer(card).data)
    serializer = CardSerializer(card, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def toggle_card_status(request, pk):
    try:
        account_ids = Account.objects.filter(user=request.user).values_list('id', flat=True)
        card = Card.objects.get(id=pk, account__in=account_ids)
    except Card.DoesNotExist:
        return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)
    card.status = 'BLOCKED' if card.status == 'ACTIVE' else 'ACTIVE'
    card.save()
    return Response(CardSerializer(card).data)


# ─── Loan Views ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def loans_list(request):
    loans = Loan.objects.filter(user=request.user)
    return Response(LoanSerializer(loans, many=True).data)


@api_view(['POST'])
def apply_loan(request):
    serializer = LoanApplicationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
        account = Account.objects.get(id=data['account_id'], user=request.user)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    interest_rate = Decimal('12.0')  # Annual
    monthly_rate = interest_rate / 12 / 100
    n = data['tenure_months']
    p = data['amount']
    if monthly_rate > 0:
        monthly = p * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
    else:
        monthly = p / n

    loan = Loan.objects.create(
        user=request.user,
        account=account,
        loan_type=data['loan_type'],
        principal_amount=p,
        outstanding_balance=p,
        interest_rate=interest_rate,
        tenure_months=n,
        monthly_installment=round(monthly, 2),
        purpose=data.get('purpose', ''),
        status='PENDING'
    )
    return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


# ─── Beneficiary Views ───────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def beneficiaries_list(request):
    if request.method == 'GET':
        return Response(BeneficiarySerializer(
            Beneficiary.objects.filter(user=request.user), many=True
        ).data)
    serializer = BeneficiarySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def beneficiary_detail(request, pk):
    try:
        b = Beneficiary.objects.get(id=pk, user=request.user)
    except Beneficiary.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(BeneficiarySerializer(b).data)
    if request.method == 'DELETE':
        b.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = BeneficiarySerializer(b, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Notifications ───────────────────────────────────────────────────────────

@api_view(['GET'])
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)[:30]
    return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['POST'])
def mark_notification_read(request, pk):
    try:
        n = Notification.objects.get(id=pk, user=request.user)
        n.is_read = True
        n.save()
        return Response(NotificationSerializer(n).data)
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})
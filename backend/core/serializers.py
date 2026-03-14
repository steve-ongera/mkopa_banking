from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Account, Transaction, Card, Loan, Beneficiary, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'gender', 'address', 'city',
            'country', 'national_id', 'profile_picture', 'is_verified',
            'two_factor_enabled', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Auto-create a savings account for the user
        Account.objects.create(
            user=user,
            account_type='SAVINGS',
            currency='USD',
            balance=0.00,
            available_balance=0.00
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class AccountSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id', 'account_number', 'account_type', 'currency',
            'balance', 'available_balance', 'interest_rate', 'status',
            'daily_limit', 'user_name', 'created_at'
        ]
        read_only_fields = ['id', 'account_number', 'balance', 'available_balance', 'created_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class TransactionSerializer(serializers.ModelSerializer):
    from_account_number = serializers.SerializerMethodField()
    to_account_number = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'transaction_type', 'amount', 'fee',
            'currency', 'status', 'description', 'balance_before',
            'balance_after', 'from_account', 'to_account',
            'from_account_number', 'to_account_number',
            'metadata', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'reference', 'status', 'balance_before', 'balance_after', 'created_at']

    def get_from_account_number(self, obj):
        return obj.from_account.account_number if obj.from_account else None

    def get_to_account_number(self, obj):
        return obj.to_account.account_number if obj.to_account else None


class DepositSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='Deposit')


class WithdrawalSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='Withdrawal')


class TransferSerializer(serializers.Serializer):
    from_account_id = serializers.UUIDField()
    to_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='Transfer')


class CardSerializer(serializers.ModelSerializer):
    masked_number = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = [
            'id', 'masked_number', 'card_type', 'network', 'card_holder_name',
            'expiry_month', 'expiry_year', 'status', 'spending_limit',
            'online_payments', 'international_transactions', 'contactless',
            'account_number', 'created_at'
        ]
        read_only_fields = ['id', 'masked_number', 'created_at']

    def get_masked_number(self, obj):
        return f"****  ****  ****  {obj.card_number[-4:]}"

    def get_account_number(self, obj):
        return obj.account.account_number


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_type', 'principal_amount', 'outstanding_balance',
            'interest_rate', 'tenure_months', 'monthly_installment',
            'status', 'purpose', 'disbursement_date', 'next_payment_date',
            'account', 'created_at'
        ]
        read_only_fields = ['id', 'outstanding_balance', 'monthly_installment', 'status', 'created_at']


class LoanApplicationSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    loan_type = serializers.ChoiceField(choices=['PERSONAL', 'MORTGAGE', 'AUTO', 'BUSINESS', 'STUDENT'])
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=100)
    tenure_months = serializers.IntegerField(min_value=1, max_value=360)
    purpose = serializers.CharField(max_length=500, required=False)


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            'id', 'name', 'account_number', 'bank_name',
            'bank_code', 'nickname', 'is_favorite', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class DashboardSerializer(serializers.Serializer):
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    accounts = AccountSerializer(many=True)
    recent_transactions = TransactionSerializer(many=True)
    unread_notifications = serializers.IntegerField()
    active_cards = serializers.IntegerField()
    active_loans = serializers.IntegerField()
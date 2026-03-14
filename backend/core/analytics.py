"""
core/analytics.py
Extra API views: spending analytics, account statement, balance history.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Account, Transaction


@api_view(["GET"])
def spending_analytics(request):
    """
    Returns monthly income/expense totals for the last 6 months,
    plus a category breakdown for the current month.
    """
    user = request.user
    account_ids = Account.objects.filter(user=user).values_list("id", flat=True)
    now = timezone.now()

    monthly = []
    for i in range(5, -1, -1):
        start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            end = now
        else:
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month.replace(day=1)

        income = Transaction.objects.filter(
            to_account__in=account_ids,
            transaction_type__in=["DEPOSIT", "INTEREST", "REFUND"],
            status="COMPLETED",
            created_at__gte=start,
            created_at__lt=end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        expenses = Transaction.objects.filter(
            from_account__in=account_ids,
            transaction_type__in=["WITHDRAWAL", "PAYMENT", "TRANSFER", "FEE"],
            status="COMPLETED",
            created_at__gte=start,
            created_at__lt=end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        monthly.append({
            "month": start.strftime("%b"),
            "year": start.year,
            "income": float(income),
            "expenses": float(expenses),
            "net": float(income - expenses),
        })

    # Current month breakdown by type
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    breakdown = Transaction.objects.filter(
        Q(from_account__in=account_ids) | Q(to_account__in=account_ids),
        status="COMPLETED",
        created_at__gte=month_start,
    ).values("transaction_type").annotate(
        total=Sum("amount"),
        count=Count("id"),
    ).order_by("-total")

    return Response({
        "monthly": monthly,
        "current_month_breakdown": list(breakdown),
    })


@api_view(["GET"])
def account_statement(request, account_id):
    """
    Full account statement with running balance for a given account.
    Query params: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    try:
        account = Account.objects.get(id=account_id, user=request.user)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=404)

    qs = Transaction.objects.filter(
        Q(from_account=account) | Q(to_account=account),
        status="COMPLETED",
    ).order_by("created_at")

    start = request.query_params.get("start_date")
    end = request.query_params.get("end_date")
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)

    statement = []
    for txn in qs:
        is_credit = txn.to_account_id == account.id
        statement.append({
            "date": txn.created_at.strftime("%Y-%m-%d %H:%M"),
            "reference": txn.reference,
            "description": txn.description or txn.transaction_type,
            "type": txn.transaction_type,
            "credit": float(txn.amount) if is_credit else None,
            "debit": float(txn.amount) if not is_credit else None,
            "balance": float(txn.balance_after),
        })

    total_credits = sum(r["credit"] or 0 for r in statement)
    total_debits = sum(r["debit"] or 0 for r in statement)

    return Response({
        "account_number": account.account_number,
        "account_type": account.account_type,
        "currency": account.currency,
        "current_balance": float(account.balance),
        "statement": statement,
        "summary": {
            "total_credits": total_credits,
            "total_debits": total_debits,
            "net": total_credits - total_debits,
            "transaction_count": len(statement),
        },
    })


@api_view(["GET"])
def balance_history(request):
    """
    Returns daily closing balance for all accounts over the last 30 days.
    Useful for sparkline charts.
    """
    user = request.user
    accounts = Account.objects.filter(user=user, status="ACTIVE")
    now = timezone.now()

    result = {}
    for acc in accounts:
        history = []
        for days_ago in range(29, -1, -1):
            day = now - timedelta(days=days_ago)
            last_txn = Transaction.objects.filter(
                Q(from_account=acc) | Q(to_account=acc),
                status="COMPLETED",
                created_at__date__lte=day.date(),
            ).order_by("-created_at").first()

            balance = float(last_txn.balance_after) if last_txn else 0.0
            history.append({"date": day.strftime("%Y-%m-%d"), "balance": balance})

        result[acc.account_number] = {
            "account_type": acc.account_type,
            "currency": acc.currency,
            "history": history,
        }

    return Response(result)
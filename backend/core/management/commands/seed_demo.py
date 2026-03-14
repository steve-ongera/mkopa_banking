"""
Management command: python manage.py seed_demo
Creates a demo user with accounts, transactions, cards, loans and notifications.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random
import string

from core.models import (
    User, Account, Transaction, Card, Loan, Beneficiary, Notification
)


def rnd_ref():
    return "TXN" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Command(BaseCommand):
    help = "Seed the database with a demo user and sample banking data"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing demo data first")

    def handle(self, *args, **options):
        if options["flush"]:
            User.objects.filter(username="demo").delete()
            self.stdout.write("Flushed existing demo data.")

        # ── Create / get demo user ────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@novapay.com",
                "first_name": "Alex",
                "last_name": "Morgan",
                "phone": "+1 555 010 2024",
                "date_of_birth": date(1992, 6, 15),
                "gender": "M",
                "address": "42 Fintech Avenue",
                "city": "San Francisco",
                "country": "USA",
                "is_verified": True,
            },
        )
        if created:
            user.set_password("Demo@1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("✔  Created demo user  (username: demo / password: Demo@1234)"))
        else:
            self.stdout.write("ℹ  Demo user already exists — skipping user creation.")

        # ── Accounts ─────────────────────────────────────────────────────────
        accounts_data = [
            ("SAVINGS",  "USD", Decimal("24580.75"),  Decimal("24580.75"),  Decimal("3.5")),
            ("CHECKING", "USD", Decimal("8340.00"),   Decimal("8340.00"),   Decimal("0.0")),
            ("BUSINESS", "USD", Decimal("105200.50"), Decimal("105200.50"), Decimal("1.5")),
        ]
        accs = []
        for acc_type, currency, balance, avail, rate in accounts_data:
            acc, _ = Account.objects.get_or_create(
                user=user,
                account_type=acc_type,
                defaults={
                    "currency": currency,
                    "balance": balance,
                    "available_balance": avail,
                    "interest_rate": rate,
                    "status": "ACTIVE",
                    "daily_limit": Decimal("50000.00"),
                },
            )
            accs.append(acc)
        self.stdout.write(self.style.SUCCESS(f"✔  {len(accs)} accounts ready"))

        primary = accs[0]
        checking = accs[1]
        business = accs[2] if len(accs) > 2 else primary

        # ── Transactions ──────────────────────────────────────────────────────
        tx_count = Transaction.objects.filter(
            from_account__in=accs
        ).count() + Transaction.objects.filter(to_account__in=accs).count()

        if tx_count < 5:
            txn_templates = [
                (None,     primary,   "DEPOSIT",    Decimal("5000.00"), "Initial deposit",         "COMPLETED"),
                (None,     primary,   "DEPOSIT",    Decimal("3200.00"), "Salary — March",           "COMPLETED"),
                (primary,  None,      "WITHDRAWAL", Decimal("200.00"),  "ATM withdrawal",           "COMPLETED"),
                (primary,  checking,  "TRANSFER",   Decimal("1500.00"), "Monthly allowance",        "COMPLETED"),
                (None,     business,  "DEPOSIT",    Decimal("12000.00"),"Client payment — Acme Co","COMPLETED"),
                (primary,  None,      "PAYMENT",    Decimal("89.99"),   "Netflix subscription",     "COMPLETED"),
                (primary,  None,      "PAYMENT",    Decimal("1200.00"), "Rent — April",             "COMPLETED"),
                (None,     checking,  "DEPOSIT",    Decimal("500.00"),  "Refund from vendor",       "COMPLETED"),
                (checking, None,      "WITHDRAWAL", Decimal("150.00"),  "Groceries",                "COMPLETED"),
                (primary,  None,      "PAYMENT",    Decimal("65.00"),   "Electricity bill",         "COMPLETED"),
                (None,     primary,   "INTEREST",   Decimal("42.30"),   "Monthly interest",         "COMPLETED"),
                (primary,  None,      "FEE",        Decimal("5.00"),    "Maintenance fee",          "COMPLETED"),
                (business, primary,   "TRANSFER",   Decimal("3000.00"), "Owner draw",               "COMPLETED"),
                (primary,  None,      "PAYMENT",    Decimal("240.00"),  "Insurance premium",        "COMPLETED"),
                (None,     primary,   "DEPOSIT",    Decimal("750.00"),  "Freelance payment",        "COMPLETED"),
                (primary,  None,      "WITHDRAWAL", Decimal("300.00"),  "Weekend cash",             "COMPLETED"),
                (primary,  checking,  "TRANSFER",   Decimal("500.00"),  "Emergency fund top-up",    "PENDING"),
                (None,     business,  "DEPOSIT",    Decimal("8500.00"), "Invoice #INV-2024-88",     "COMPLETED"),
            ]

            base_time = timezone.now() - timedelta(days=45)
            for i, (frm, to, tx_type, amount, desc, status) in enumerate(txn_templates):
                bal_before = (frm or to).balance
                Transaction.objects.create(
                    reference=rnd_ref(),
                    from_account=frm,
                    to_account=to,
                    transaction_type=tx_type,
                    amount=amount,
                    fee=round(amount * Decimal("0.001"), 2) if tx_type == "TRANSFER" else Decimal("0.00"),
                    currency="USD",
                    status=status,
                    description=desc,
                    balance_before=bal_before,
                    balance_after=bal_before,
                    completed_at=timezone.now() if status == "COMPLETED" else None,
                    created_at=base_time + timedelta(days=i * 2, hours=random.randint(8, 20)),
                )
            self.stdout.write(self.style.SUCCESS(f"✔  {len(txn_templates)} transactions created"))
        else:
            self.stdout.write("ℹ  Transactions already exist — skipping.")

        # ── Cards ─────────────────────────────────────────────────────────────
        cards_data = [
            (primary,  "DEBIT",  "VISA",       "4532 0151 1234 5678", 12, 2027, Decimal("5000.00"),  True,  False, "ACTIVE"),
            (checking, "DEBIT",  "MASTERCARD", "5425 2334 5678 9012", 8,  2026, Decimal("3000.00"),  True,  True,  "ACTIVE"),
            (primary,  "CREDIT", "VISA",       "4916 1234 5678 9012", 3,  2028, Decimal("10000.00"), True,  True,  "ACTIVE"),
            (business, "DEBIT",  "MASTERCARD", "5200 8282 8282 8210", 6,  2026, Decimal("20000.00"), True,  True,  "BLOCKED"),
        ]
        card_count = Card.objects.filter(account__in=accs).count()
        if card_count < 2:
            holder = f"{user.first_name} {user.last_name}".upper()
            for acc, ctype, network, number, exp_m, exp_y, limit, online, intl, status in cards_data:
                num_clean = number.replace(" ", "")
                Card.objects.get_or_create(
                    card_number=num_clean,
                    defaults={
                        "account": acc,
                        "card_type": ctype,
                        "network": network,
                        "card_holder_name": holder,
                        "expiry_month": exp_m,
                        "expiry_year": exp_y,
                        "cvv_hash": "hashed_cvv_placeholder",
                        "status": status,
                        "spending_limit": limit,
                        "online_payments": online,
                        "international_transactions": intl,
                        "contactless": True,
                    },
                )
            self.stdout.write(self.style.SUCCESS(f"✔  {len(cards_data)} cards created"))
        else:
            self.stdout.write("ℹ  Cards already exist — skipping.")

        # ── Loans ─────────────────────────────────────────────────────────────
        loan_count = Loan.objects.filter(user=user).count()
        if loan_count < 1:
            loans_data = [
                ("PERSONAL", Decimal("15000.00"), Decimal("11200.00"), Decimal("12.0"), 24, Decimal("705.55"), "ACTIVE",  "Home renovation",     date.today() - timedelta(days=180), date.today() + timedelta(days=15)),
                ("AUTO",     Decimal("28000.00"), Decimal("22400.00"), Decimal("8.5"),  60, Decimal("574.20"), "ACTIVE",  "Toyota Corolla 2023", date.today() - timedelta(days=120), date.today() + timedelta(days=10)),
                ("PERSONAL", Decimal("5000.00"),  Decimal("5000.00"),  Decimal("14.0"), 12, Decimal("448.40"), "PENDING", "Medical expenses",    None,                              None),
            ]
            for ltype, principal, outstanding, rate, tenure, emi, status, purpose, disburse, next_pay in loans_data:
                Loan.objects.create(
                    user=user,
                    account=primary,
                    loan_type=ltype,
                    principal_amount=principal,
                    outstanding_balance=outstanding,
                    interest_rate=rate,
                    tenure_months=tenure,
                    monthly_installment=emi,
                    status=status,
                    purpose=purpose,
                    disbursement_date=disburse,
                    next_payment_date=next_pay,
                )
            self.stdout.write(self.style.SUCCESS(f"✔  {len(loans_data)} loans created"))
        else:
            self.stdout.write("ℹ  Loans already exist — skipping.")

        # ── Beneficiaries ─────────────────────────────────────────────────────
        bene_count = Beneficiary.objects.filter(user=user).count()
        if bene_count < 1:
            benes = [
                ("Sarah Johnson",   "201934567890", "Chase Bank",      "Mom",        True),
                ("David Lee",       "304851234567", "Bank of America", "Landlord",   False),
                ("Emma Wilson",     "102938475610", "Wells Fargo",     "Emma",       True),
                ("Tech Corp Ltd",   "987654321098", "Citi Bank",       "Office Rent",False),
                ("James Martinez",  "112233445566", "NovaPay",         "James",      False),
            ]
            for name, acct, bank, nick, fav in benes:
                Beneficiary.objects.create(
                    user=user,
                    name=name,
                    account_number=acct,
                    bank_name=bank,
                    nickname=nick,
                    is_favorite=fav,
                )
            self.stdout.write(self.style.SUCCESS(f"✔  {len(benes)} beneficiaries created"))
        else:
            self.stdout.write("ℹ  Beneficiaries already exist — skipping.")

        # ── Notifications ─────────────────────────────────────────────────────
        notif_count = Notification.objects.filter(user=user).count()
        if notif_count < 1:
            notifs = [
                ("Transaction Alert",      "Your account received $3,200.00 salary deposit.",                    "TRANSACTION", False),
                ("Security Notice",        "New login detected from San Francisco, CA. If not you, contact us.", "SECURITY",    False),
                ("Loan EMI Reminder",      "Your loan EMI of $705.55 is due in 5 days.",                         "SYSTEM",      False),
                ("Card Blocked",           "Your Business Mastercard ending 8210 has been blocked.",              "SECURITY",    True),
                ("Transfer Successful",    "You transferred $1,500 to checking account successfully.",            "TRANSACTION", True),
                ("Special Offer",          "Get 0% interest on personal loans up to $20,000 this month!",        "PROMO",       True),
                ("Password Changed",       "Your account password was updated successfully.",                     "SECURITY",    True),
                ("Monthly Statement",      "Your March 2024 account statement is ready for download.",            "SYSTEM",      True),
                ("Bill Payment Confirmed", "Electricity bill of $65.00 paid successfully.",                       "TRANSACTION", True),
                ("Interest Credited",      "$42.30 interest has been credited to your savings account.",          "TRANSACTION", True),
            ]
            for title, msg, ntype, read in notifs:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=msg,
                    notification_type=ntype,
                    is_read=read,
                )
            self.stdout.write(self.style.SUCCESS(f"✔  {len(notifs)} notifications created"))
        else:
            self.stdout.write("ℹ  Notifications already exist — skipping.")

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("  Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(f"  Username : demo")
        self.stdout.write(f"  Password : Demo@1234")
        self.stdout.write(f"  Email    : demo@novapay.com")
        self.stdout.write(self.style.SUCCESS("=" * 50))
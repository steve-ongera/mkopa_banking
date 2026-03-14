from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import random
import string


def generate_account_number():
    return ''.join(random.choices(string.digits, k=12))


def generate_card_number():
    return ''.join(random.choices(string.digits, k=16))


class User(AbstractUser):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.email})"


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings Account'),
        ('CHECKING', 'Checking Account'),
        ('BUSINESS', 'Business Account'),
        ('FIXED', 'Fixed Deposit'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('FROZEN', 'Frozen'),
        ('CLOSED', 'Closed'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('KES', 'Kenyan Shilling'),
        ('NGN', 'Nigerian Naira'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True, default=generate_account_number)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='SAVINGS')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
        ('PAYMENT', 'Payment'),
        ('REFUND', 'Refund'),
        ('FEE', 'Fee'),
        ('INTEREST', 'Interest'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=50, unique=True)
    from_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='outgoing_transactions'
    )
    to_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incoming_transactions'
    )
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.amount}"


class Card(models.Model):
    CARD_TYPES = [('DEBIT', 'Debit'), ('CREDIT', 'Credit'), ('PREPAID', 'Prepaid')]
    CARD_NETWORKS = [('VISA', 'Visa'), ('MASTERCARD', 'Mastercard'), ('AMEX', 'Amex')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('BLOCKED', 'Blocked'), ('EXPIRED', 'Expired'), ('PENDING', 'Pending')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=19, unique=True)
    card_type = models.CharField(max_length=10, choices=CARD_TYPES)
    network = models.CharField(max_length=12, choices=CARD_NETWORKS, default='VISA')
    card_holder_name = models.CharField(max_length=100)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvv_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    spending_limit = models.DecimalField(max_digits=15, decimal_places=2, default=5000.00)
    online_payments = models.BooleanField(default=True)
    international_transactions = models.BooleanField(default=False)
    contactless = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cards'

    def __str__(self):
        return f"****{self.card_number[-4:]} - {self.card_holder_name}"


class Loan(models.Model):
    LOAN_TYPES = [
        ('PERSONAL', 'Personal Loan'),
        ('MORTGAGE', 'Mortgage'),
        ('AUTO', 'Auto Loan'),
        ('BUSINESS', 'Business Loan'),
        ('STUDENT', 'Student Loan'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('PAID', 'Fully Paid'),
        ('DEFAULTED', 'Defaulted'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=15, choices=LOAN_TYPES)
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.IntegerField()
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')
    purpose = models.TextField(blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'

    def __str__(self):
        return f"Loan {self.id} - {self.user.username}"


class Beneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='beneficiaries')
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=20, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beneficiaries'

    def __str__(self):
        return f"{self.name} - {self.account_number}"


class Notification(models.Model):
    TYPES = [
        ('TRANSACTION', 'Transaction'),
        ('SECURITY', 'Security'),
        ('PROMO', 'Promotional'),
        ('SYSTEM', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
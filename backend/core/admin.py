from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Account, Transaction, Card, Loan, Beneficiary, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_verified', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Banking Info', {'fields': ('phone', 'date_of_birth', 'gender', 'address', 'city', 'country', 'national_id', 'is_verified', 'two_factor_enabled')}),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'user', 'account_type', 'currency', 'balance', 'status']
    list_filter = ['account_type', 'currency', 'status']
    search_fields = ['account_number', 'user__username']
    readonly_fields = ['id', 'account_number', 'created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'transaction_type', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'currency']
    search_fields = ['reference']
    readonly_fields = ['id', 'reference', 'created_at']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'card_holder_name', 'card_type', 'network', 'status']
    list_filter = ['card_type', 'network', 'status']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'loan_type', 'principal_amount', 'outstanding_balance', 'status']
    list_filter = ['loan_type', 'status']
    actions = ['approve_loans', 'reject_loans']

    def approve_loans(self, request, queryset):
        queryset.filter(status='PENDING').update(status='APPROVED')
    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        queryset.filter(status='PENDING').update(status='REJECTED')
    reject_loans.short_description = "Reject selected loans"


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_number', 'bank_name', 'user']
    search_fields = ['name', 'account_number']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
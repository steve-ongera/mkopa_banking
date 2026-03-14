from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import analytics

urlpatterns = [
    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Accounts
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/<uuid:pk>/', views.account_detail, name='account_detail'),

    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/<uuid:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/deposit/', views.deposit, name='deposit'),
    path('transactions/withdraw/', views.withdraw, name='withdraw'),
    path('transactions/transfer/', views.transfer, name='transfer'),

    # Cards
    path('cards/', views.cards_list, name='cards_list'),
    path('cards/<uuid:pk>/', views.card_detail, name='card_detail'),
    path('cards/<uuid:pk>/toggle/', views.toggle_card_status, name='toggle_card'),

    # Loans
    path('loans/', views.loans_list, name='loans_list'),
    path('loans/apply/', views.apply_loan, name='apply_loan'),

    # Beneficiaries
    path('beneficiaries/', views.beneficiaries_list, name='beneficiaries_list'),
    path('beneficiaries/<int:pk>/', views.beneficiary_detail, name='beneficiary_detail'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # Analytics
    path('analytics/spending/', analytics.spending_analytics, name='spending_analytics'),
    path('analytics/statement/<uuid:account_id>/', analytics.account_statement, name='account_statement'),
    path('analytics/balance-history/', analytics.balance_history, name='balance_history'),
]
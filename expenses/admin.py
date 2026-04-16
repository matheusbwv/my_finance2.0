from django.contrib import admin
from .models import Account, Debt, Transaction

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_amount', 'paid_amount', 'debt_type', 'status')
    list_filter = ('debt_type', 'status')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'transaction_type', 'account')
    list_filter = ('transaction_type', 'account', 'date')
    search_fields = ('title', 'category')

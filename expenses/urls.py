from django.urls import path
from .views import (
    DashboardView, TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView,
    AccountCreateView, AccountUpdateView, AccountDeleteView, DebtCreateView, import_nubank_csv, bulk_delete_transactions
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('importar-extrato/', import_nubank_csv, name='import-csv'),
    path('transacoes/deletar-massa/', bulk_delete_transactions, name='transaction-bulk-delete'),
    
    # Transações
    path('transacoes/', TransactionListView.as_view(), name='transaction-list'),
    path('transacoes/nova/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transacoes/<int:pk>/editar/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transacoes/<int:pk>/deletar/', TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Contas
    path('contas/nova/', AccountCreateView.as_view(), name='account-create'),
    path('contas/<int:pk>/editar/', AccountUpdateView.as_view(), name='account-update'),
    path('contas/<int:pk>/deletar/', AccountDeleteView.as_view(), name='account-delete'),
    
    # Dívidas
    path('dividas/nova/', DebtCreateView.as_view(), name='debt-create'),
]

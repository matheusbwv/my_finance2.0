from django.urls import path
from .views import (
    DashboardView, TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView,
    AccountCreateView, DebtCreateView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Transações
    path('transacoes/', TransactionListView.as_view(), name='transaction-list'),
    path('transacoes/nova/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transacoes/<int:pk>/editar/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transacoes/<int:pk>/deletar/', TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Contas
    path('contas/nova/', AccountCreateView.as_view(), name='account-create'),
    
    # Dívidas
    path('dividas/nova/', DebtCreateView.as_view(), name='debt-create'),
]

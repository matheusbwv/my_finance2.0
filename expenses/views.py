from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Sum
from datetime import datetime
from .models import Account, Debt, Transaction
from .forms import AccountForm, DebtForm, TransactionForm

class DashboardView(TemplateView):
    template_name = 'expenses/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtro de Mês e Ano
        month = self.request.GET.get('month', datetime.now().month)
        year = self.request.GET.get('year', datetime.now().year)
        
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            month = datetime.now().month
            year = datetime.now().year

        transactions_month = Transaction.objects.filter(date__month=month, date__year=year)
        
        context['total_income'] = transactions_month.filter(transaction_type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_expense'] = transactions_month.filter(transaction_type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['balance_month'] = context['total_income'] - context['total_expense']
        
        context['accounts'] = Account.objects.all()
        context['total_balance'] = Account.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        
        context['active_debts'] = Debt.objects.filter(status='ACTIVE')
        context['total_debts'] = sum(d.remaining_amount for d in context['active_debts'])
        
        context['recent_transactions'] = Transaction.objects.all()[:10]
        context['current_month'] = month
        context['current_year'] = year
        
        # Lista de meses para o filtro
        context['months_range'] = range(1, 13)
        return context

# Views para Transações
class TransactionListView(ListView):
    model = Transaction
    template_name = 'expenses/transaction_list.html'
    context_object_name = 'transactions'

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'expenses/transaction_form.html'
    success_url = reverse_lazy('dashboard')

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'expenses/transaction_form.html'
    success_url = reverse_lazy('dashboard')

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'expenses/transaction_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

# Views para Contas
class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'expenses/account_form.html'
    success_url = reverse_lazy('dashboard')

# Views para Dívidas
class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'expenses/debt_form.html'
    success_url = reverse_lazy('dashboard')

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Sum
from datetime import datetime
from .models import Account, Debt, Transaction
from .forms import AccountForm, DebtForm, TransactionForm

import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Account, Debt, Transaction

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

def import_nubank_csv(request):
    accounts = Account.objects.all()
    
    if request.method == 'POST':
        account_id = request.POST.get('account')
        csv_file = request.FILES.get('file')
        
        if not account_id or not csv_file:
            messages.error(request, "Por favor, selecione uma conta e um arquivo.")
            return redirect('import-csv')
            
        account = get_object_or_404(Account, id=account_id)
        
        try:
            # Lendo o arquivo CSV
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            skipped_count = 0
            
            for row in reader:
                # Mapeamento das colunas do Nubank: Data, Valor, Identificador, Descrição
                date_str = row.get('Data')
                amount_raw = row.get('Valor')
                description = row.get('Descrição')
                
                if not date_str or not amount_raw:
                    continue
                
                # Converter Data (01/04/2026 -> 2026-04-01)
                date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                
                # Converter Valor (-9.48 -> 9.48 e tipo IN/OUT)
                amount_float = float(amount_raw)
                transaction_type = 'IN' if amount_float > 0 else 'OUT'
                final_amount = abs(amount_float)
                
                # Categoria Padrão baseada na descrição
                category = "Importado (Nubank)"
                if "Pix" in description:
                    category = "Transferência Pix"
                elif "Fatura" in description or "Pagamento" in description:
                    category = "Pagamentos"
                elif "Compra" in description:
                    category = "Compras"
                
                # Verificar se já existe para evitar duplicata
                exists = Transaction.objects.filter(
                    account=account,
                    date=date_obj,
                    amount=final_amount,
                    title=description[:200]
                ).exists()
                
                if not exists:
                    Transaction.objects.create(
                        account=account,
                        date=date_obj,
                        amount=final_amount,
                        transaction_type=transaction_type,
                        title=description[:200],
                        category=category
                    )
                    created_count += 1
                else:
                    skipped_count += 1
            
            messages.success(request, f"Importação concluída! {created_count} novas transações adicionadas. {skipped_count} duplicatas ignoradas.")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Erro ao processar arquivo: {str(e)}")
            return redirect('import-csv')

    return render(request, 'expenses/import_csv.html', {'accounts': accounts})

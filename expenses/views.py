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
        
        # 1. Calcular saldo real para cada conta (Considerando TODO o histórico)
        accounts = Account.objects.all()
        total_balance = 0
        
        for acc in accounts:
            all_transactions = Transaction.objects.filter(account=acc)
            income = all_transactions.filter(transaction_type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
            expense = all_transactions.filter(transaction_type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
            acc.real_balance = acc.balance + income - expense
            total_balance += acc.real_balance
            
        context['accounts'] = accounts
        context['total_balance'] = total_balance

        # 2. Filtro de Mês e Ano para os outros cards (Receitas/Despesas do período)
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
        
        context['active_debts'] = Debt.objects.filter(status='ACTIVE')
        context['total_debts'] = sum(d.remaining_amount for d in context['active_debts'])
        
        context['recent_transactions'] = Transaction.objects.all().order_by('-date')[:10]
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
    ordering = ['-date']

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

class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'expenses/account_form.html'
    success_url = reverse_lazy('dashboard')

class AccountDeleteView(DeleteView):
    model = Account
    template_name = 'expenses/transaction_confirm_delete.html'
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
            # Lendo o arquivo CSV com suporte a UTF-8-SIG (para remover o BOM se existir)
            file_data = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(file_data)
            
            # Tenta ler com vírgula primeiro, se falhar ou encontrar apenas 1 coluna, tenta ponto e vírgula
            content = io_string.read()
            io_string.seek(0)
            
            delimiter = ','
            if ';' in content and (content.count(';') > content.count(',')):
                delimiter = ';'
            
            reader = csv.DictReader(io_string, delimiter=delimiter)
            
            # Limpa os nomes das colunas (remove espaços extras)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            created_count = 0
            skipped_count = 0
            
            for row in reader:
                # 1. Detectar o tipo de extrato pelas colunas presentes
                is_credit = 'date' in reader.fieldnames and 'title' in reader.fieldnames
                
                if is_credit:
                    # Formato Cartão de Crédito: date,title,amount
                    date_str = row.get('date')
                    amount_raw = row.get('amount')
                    description = row.get('title')
                    identifier = f"credit-{date_str}-{description}-{amount_raw}" # Geramos um ID único para crédito
                    date_format = '%Y-%m-%d'
                else:
                    # Formato Conta (Pix): Data,Valor,Identificador,Descrição
                    date_str = row.get('Data') or row.get('data')
                    amount_raw = row.get('Valor') or row.get('valor')
                    description = row.get('Descrição') or row.get('descricao') or row.get('Description')
                    identifier = row.get('Identificador') or row.get('identificador') or row.get('Identifier')
                    date_format = '%d/%m/%Y'
                
                if not date_str or not amount_raw:
                    continue
                
                try:
                    # Converter Data
                    date_obj = datetime.strptime(date_str.strip(), date_format).date()
                    
                    # Converter Valor
                    amount_clean = amount_raw.strip().replace(',', '.')
                    amount_float = float(amount_clean)
                    
                    if is_credit:
                        # No Crédito: Positivo é GASTO, Negativo é PAGAMENTO/ESTORNO
                        transaction_type = 'OUT' if amount_float > 0 else 'IN'
                        category = "Cartão de Crédito"
                        # Ignorar "Pagamento recebido" no crédito para não duplicar com a saída da conta
                        if "Pagamento recebido" in description:
                            continue
                    else:
                        # Na Conta: Negativo é GASTO, Positivo é GANHO
                        transaction_type = 'IN' if amount_float > 0 else 'OUT'
                        category = "Pix" if "Pix" in description else "Importado"

                    final_amount = abs(amount_float)
                    title = description.strip()[:200]
                    
                    # Verifica duplicata
                    exists = False
                    if identifier:
                        exists = Transaction.objects.filter(identifier=identifier.strip()).exists()
                    
                    if not exists:
                        exists = Transaction.objects.filter(
                            account=account,
                            date=date_obj,
                            amount=final_amount,
                            title=title
                        ).exists()
                    
                    if not exists:
                        Transaction.objects.create(
                            account=account,
                            date=date_obj,
                            amount=final_amount,
                            transaction_type=transaction_type,
                            title=title,
                            category=category,
                            identifier=identifier.strip() if identifier else None
                        )
                        created_count += 1
                    else:
                        skipped_count += 1
                except (ValueError, TypeError) as e:
                    continue
            
            messages.success(request, f"Processamento concluído: {created_count} novas, {skipped_count} duplicatas.")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Erro ao processar arquivo: {str(e)}")
            return redirect('import-csv')

    return render(request, 'expenses/import_csv.html', {'accounts': accounts})

def bulk_delete_transactions(request):
    if request.method == 'POST':
        transaction_ids = request.POST.getlist('transaction_ids')
        if transaction_ids:
            deleted_count = Transaction.objects.filter(id__in=transaction_ids).delete()[0]
            messages.success(request, f"{deleted_count} transações foram excluídas com sucesso.")
        else:
            messages.warning(request, "Nenhuma transação foi selecionada.")
    return redirect('transaction-list')

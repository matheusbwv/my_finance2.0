from django import forms
from .models import Account, Debt, Transaction

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'balance', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'color': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'color'}),
        }

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['title', 'total_amount', 'paid_amount', 'debt_type', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'debt_type': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'date', 'transaction_type', 'category', 'account', 'debt', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'date'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'category': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'account': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'debt': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 2}),
        }

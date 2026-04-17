from django.db import models

class Account(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome do Banco/Conta")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Atual")
    color = models.CharField(max_length=7, default="#8a2be2", help_text="Código Hex da cor")

    def __str__(self):
        return f"{self.name} (R$ {self.balance})"

    class Meta:
        verbose_name = "Conta/Banco"
        verbose_name_plural = "Contas/Bancos"

class Debt(models.Model):
    TYPE_CHOICES = [
        ('FIXA', 'Fixa'),
        ('TEMP', 'Temporária'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Ativa'),
        ('PAID', 'Paga'),
    ]
    title = models.CharField(max_length=200, verbose_name="Título da Dívida")
    creditor = models.CharField(max_length=150, blank=True, null=True, verbose_name="Credor (Para quem deve?)")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Pago")
    debt_type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='TEMP')
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='ACTIVE')
    due_date = models.DateField(null=True, blank=True, verbose_name="Data de Vencimento")

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"{self.title} ({self.get_debt_type_display()})"

    class Meta:
        verbose_name = "Dívida"
        verbose_name_plural = "Dívidas"

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Receita (Entrada)'),
        ('OUT', 'Despesa (Saída)'),
    ]
    title = models.CharField(max_length=200, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor")
    date = models.DateField(verbose_name="Data")
    transaction_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='OUT')
    category = models.CharField(max_length=100, verbose_name="Categoria")
    identifier = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="ID da Transação")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions', verbose_name="Conta/Banco")
    debt = models.ForeignKey(Debt, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Vincular a Dívida")
    description = models.TextField(blank=True, verbose_name="Notas adicionais")

    def __str__(self):
        prefix = "+" if self.transaction_type == 'IN' else "-"
        return f"{prefix} R$ {self.amount} - {self.title}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

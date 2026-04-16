from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    account = instance.account
    if created:
        if instance.transaction_type == 'IN':
            account.balance += instance.amount
        else:
            account.balance -= instance.amount
    else:
        # Lógica para atualização de transação existente (opcional/complexa)
        # Para simplificar agora, focaremos em novas transações
        pass
    account.save()

@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    account = instance.account
    if instance.transaction_type == 'IN':
        account.balance -= instance.amount
    else:
        account.balance += instance.amount
    account.save()

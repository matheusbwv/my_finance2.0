from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    # Desativamos a alteração direta no banco para evitar contagem dupla
    # O saldo agora é calculado dinamicamente na DashboardView
    pass

@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    # Desativamos a alteração direta no banco para evitar contagem dupla
    pass

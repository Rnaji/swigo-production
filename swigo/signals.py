from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Tournee

@receiver(pre_delete, sender=Tournee)
def liberer_livreur_si_tournee_supprimee(sender, instance, **kwargs):
    if instance.livreur:
        instance.livreur.is_booked = False
        instance.livreur.save(update_fields=['is_booked'])

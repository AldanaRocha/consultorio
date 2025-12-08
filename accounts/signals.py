# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from turnos.models import PacienteProfile, MedicoProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profiles(sender, instance, created, **kwargs):
    if created:
        # por defecto no asumimos rol; los perfiles se crean cuando se asigna grupo
        pass

# Si quieres crear perfiles al asignar grupos, se puede ampliar.

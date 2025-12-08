# accounts/utils.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def create_default_groups():
    # Llamar desde un migration o desde admin shell
    groups = ['Paciente', 'Recepcionista', 'Medico', 'Director']
    for g in groups:
        Group.objects.get_or_create(name=g)

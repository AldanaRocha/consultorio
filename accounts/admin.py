from django.apps import AppConfig
from django.contrib.auth.models import Group

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        Group.objects.get_or_create(name='Director')

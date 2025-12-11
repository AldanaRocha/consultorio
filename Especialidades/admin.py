from django.contrib import admin
from .models import Especialidad


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "descripcion")
    fields = ("tipo", "descripcion") 

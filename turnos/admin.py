# turnos/admin.py
from django.contrib import admin
from .models import Turno, MedicoProfile, PacienteProfile
admin.site.register([Turno, MedicoProfile, PacienteProfile])

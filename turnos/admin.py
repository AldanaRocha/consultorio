# turnos/admin.py
from django.contrib import admin
from .models import Turno, Especialidad, MedicoProfile, PacienteProfile
admin.site.register([Turno, Especialidad, MedicoProfile, PacienteProfile])

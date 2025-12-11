from django.contrib import admin
from Especialidades.models import Especialidad

admin.site.index_title = "Panel Administrativo del Director"
admin.site.site_header = "Consultorio Médico"
admin.site.site_title = "Panel del Director"




# Ocultar el modelo Especialidad del admin
admin.site.unregister(Especialidad)
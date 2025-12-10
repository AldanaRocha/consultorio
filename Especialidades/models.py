# Especialidad/models.py
from django.db import models

class Especialidad(models.Model):
    tipo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo

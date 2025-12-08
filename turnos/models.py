# turnos/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse

User = settings.AUTH_USER_MODEL

ESTADO_TURNO = [
    ('pendiente', 'Pendiente'),
    ('confirmado', 'Confirmado'),
    ('en_curso', 'En curso'),
    ('atendido', 'Atendido'),
    ('cancelado', 'Cancelado'),
]

class Especialidad(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class MedicoProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medico_profile')
    matricula = models.CharField(max_length=50, blank=True)
    especialidades = models.ManyToManyField(Especialidad, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Dr/a {self.user.get_full_name() or self.user.username}"

class PacienteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente_profile')
    dni = models.CharField(max_length=30, blank=True)
    nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Turno(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='turnos_paciente')
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos_medico')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos_creados_por')
    estado = models.CharField(max_length=20, choices=ESTADO_TURNO, default='pendiente')
    asistencia_confirmada = models.BooleanField(default=False)  # la recepcionista marca cuando llega
    notificado_medico = models.BooleanField(default=False)      # la recepcionista puede avisar
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"{self.paciente} - {self.fecha_hora} - {self.estado}"

    def get_absolute_url(self):
        return reverse('detalle_turno', args=[self.pk])

# turnos/forms.py
from django import forms
from .models import Turno
from django.contrib.auth.models import User, Group

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = "__all__"
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # FILTRAR SOLO MÉDICOS
        try:
            grupo_medicos = Group.objects.get(name="Medico")
            self.fields['medico'].queryset = User.objects.filter(groups=grupo_medicos)
        except Group.DoesNotExist:
            pass

        # CAMPOS QUE EL PACIENTE NO PUEDE VER
        if user and user.groups.filter(name="Paciente").exists():
            for campo in ["paciente", "estado", "asistencia_confirmada", "notificado_medico", "creado_por"]:
                if campo in self.fields:
                    self.fields.pop(campo)

# turnos/forms.py
from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = Turno
        fields = ['especialidad','medico','fecha_hora','observaciones']

# turnos/analytics.py
from django.db.models import Count
from .models import Turno, Especialidad
def resumen_turnos_por_especialidad():
    qs = Turno.objects.values('especialidad__nombre').annotate(total=Count('id')).order_by('-total')
    return qs
def resumen_turnos_por_medico():
    qs = Turno.objects.values('medico__username','medico__first_name','medico__last_name').annotate(total=Count('id')).order_by('-total')
    return qs

from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    path('crear/', views.CrearTurnoView.as_view(), name='crear_turno'),

    # Paciente
    path('mis/', views.MisTurnosView.as_view(), name='mis_turnos'),

    # Recepcionista
    path('recepcion/all/', views.TurnosRecepcionView.as_view(), name='turnos_recepcion'),
    path('recepcion/asistencia/<int:pk>/', views.MarcarAsistenciaView.as_view(), name='marcar_asistencia'),
    path('editar/<int:pk>/', views.EditarTurnoView.as_view(), name='editar_turno'),

    # Director
    path('director/all/', views.TurnosDirectorView.as_view(), name='turnos_director'),

    # Médico
    path('medico/mis/', views.TurnosMedicoView.as_view(), name='turnos_medico'),
    path('medico/estado/<int:pk>/', views.CambiarEstadoTurnoView.as_view(), name='cambiar_estado_turno'),
]

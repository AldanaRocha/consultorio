# turnos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Turno, Especialidad
from .forms import TurnoForm
from accounts.mixins import GroupRequiredMixin
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Paciente: crear turno
class CrearTurnoView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/crear_turno.html'
    success_url = reverse_lazy('mis_turnos')
    group_required = 'Paciente'

    def form_valid(self, form):
        turno = form.save(commit=False)
        turno.paciente = self.request.user
        turno.creado_por = self.request.user
        turno.save()
        return super().form_valid(form)

# Paciente: ver sus turnos (y redirect al loguearse)
class MisTurnosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/mis_turnos.html'
    context_object_name = 'turnos'
    group_required = 'Paciente'

    def get_queryset(self):
        return Turno.objects.filter(paciente=self.request.user).order_by('fecha_hora')

# Recepcionista: ver todos los turnos (próximo->lejos)
class TurnosRecepcionView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turnos_recepcion.html'
    context_object_name = 'turnos'
    group_required = 'Recepcionista'

    def get_queryset(self):
        # filtramos turnos desde ahora en adelante, orden ascendente
        return Turno.objects.filter(fecha_hora__gte=timezone.now()).order_by('fecha_hora')

# Recepcionista: marcar asistencia y notificar medico (ajax)
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

@method_decorator(require_POST, name='dispatch')
class MarcarAsistenciaView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = 'Recepcionista'
    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        accion = request.POST.get('accion')
        if accion == 'llego':
            turno.asistencia_confirmada = True
            turno.save()
            # Aquí podrías enviar notificación (email/signal)
            return JsonResponse({'ok': True, 'msg': 'Asistencia marcada.'})
        return JsonResponse({'ok': False}, status=400)

# Medico: lista simple de sus turnos
class TurnosMedicoView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turnos_medico.html'
    context_object_name = 'turnos'
    group_required = 'Medico'

    def get_queryset(self):
        return Turno.objects.filter(medico=self.request.user, fecha_hora__gte=timezone.now()).order_by('fecha_hora')

# Medico: cambiar estado (atendido/pendiente)
class CambiarEstadoTurnoView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = 'Medico'
    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, medico=request.user)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(ESTADO_TURNO):
            turno.estado = nuevo_estado
            # si es atendido, lo ocultamos (podés filtrar en la vista)
            turno.save()
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False}, status=400)

# Director: crear médico (vista protegida)
from django.contrib.auth.forms import UserCreationForm
class CrearMedicoView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/crear_medico.html'
    success_url = reverse_lazy('dashboard_director')
    group_required = 'Director'

    def form_valid(self, form):
        user = form.save()
        # asignar grupo Medico
        from django.contrib.auth.models import Group
        medico_group = Group.objects.get(name='Medico')
        user.groups.add(medico_group)
        # crear MedicoProfile si quieres
        return super().form_valid(form)


@login_required
def home_redirect(request):
    user = request.user

    if user.groups.filter(name="Paciente").exists():
        return redirect("mis_turnos")
    elif user.groups.filter(name="Recepcionista").exists():
        return redirect("turnos_recepcion")
    elif user.groups.filter(name="Medico").exists():
        return redirect("turnos_medico")
    elif user.groups.filter(name="Director").exists():
        return redirect("admin:index")

    return redirect("login")  # fallback
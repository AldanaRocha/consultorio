# turnos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse
from .models import Turno, Especialidad, ESTADO_TURNO

from .models import Turno
from .forms import TurnoForm
from accounts.mixins import GroupRequiredMixin

# -------------------------
# HOME
# -------------------------
def home(request):
    return render(request, 'home/home.html')


@login_required
def home_redirect(request):
    user = request.user

    if user.groups.filter(name="Paciente").exists():
        return redirect('turnos:mis_turnos')

    if user.groups.filter(name="Recepcionista").exists():
        return redirect('turnos:turnos_recepcion')

    if user.groups.filter(name="Medico").exists():
        return redirect('turnos:turnos_medico')

    if user.groups.filter(name="Director").exists() or user.is_superuser:
        return redirect('turnos:turnos_recepcion')

    return redirect('home')

# -------------------------
# PACIENTE
# -------------------------
# en turnos/views.py (fragmento)
class CrearTurnoView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/crear_turno.html'
    group_required = ['Paciente', 'Recepcionista', 'Director']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # pasar user al form ✔
        return kwargs

    def form_valid(self, form):
        turno = form.save(commit=False)

        # Si quien crea es un PACIENTE → asignar automáticamente
        if self.request.user.groups.filter(name='Paciente').exists():
            turno.paciente = self.request.user

        turno.creado_por = self.request.user
        turno.save()
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if user.groups.filter(name='Paciente').exists():
            return reverse_lazy('turnos:mis_turnos')

        return reverse_lazy('turnos:turnos_recepcion')


class MisTurnosView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/mis_turnos.html'
    context_object_name = 'turnos'
    group_required = 'Paciente'

    def get_queryset(self):
        return Turno.objects.filter(
            paciente=self.request.user
        ).order_by('fecha_hora')


# -------------------------
# DIRECTOR
# -------------------------

class TurnosDirectorView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turnos_director.html'
    context_object_name = 'turnos'
    group_required = 'Director'

    def get_queryset(self):
        return Turno.objects.all().order_by('fecha_hora')


# -------------------------
# RECEPCIONISTA
# -------------------------

class TurnosRecepcionView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turnos_recepcion.html'
    context_object_name = 'turnos'
    group_required = ['Recepcionista', 'Director']

    def get_queryset(self):
        return Turno.objects.filter(
            fecha_hora__gte=timezone.now()
        ).order_by('fecha_hora')


@method_decorator(require_POST, name='dispatch')
class MarcarAsistenciaView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = 'Recepcionista'

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        accion = request.POST.get('accion')

        if accion == 'llego':
            turno.asistencia_confirmada = True
            turno.save()
            return JsonResponse({'ok': True, 'msg': 'Asistencia marcada.'})

        return JsonResponse({'ok': False}, status=400)


# -------------------------
# MÉDICO
# -------------------------

class TurnosMedicoView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turnos_medico.html'
    context_object_name = 'turnos'
    group_required = 'Medico'

    def get_queryset(self):
        return Turno.objects.filter(
            medico=self.request.user,
            fecha_hora__gte=timezone.now()
        ).order_by('fecha_hora')


class CambiarEstadoTurnoView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = 'Medico'

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)

        # 🔴 Validación correcta
        if turno.medico != request.user:
            return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

        nuevo_estado = request.POST.get('estado')

        estados_validos = dict(turno._meta.get_field('estado').choices)

        if nuevo_estado in estados_validos:
            turno.estado = nuevo_estado
            turno.save()
            return JsonResponse({'ok': True})

        return JsonResponse({'ok': False}, status=400)

# -------------------------
# OTROS
# -------------------------

@login_required
def lista_turnos(request):
    turnos = Turno.objects.all()
    return render(request, "turnos/lista.html", {"turnos": turnos})

class EditarTurnoView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = "turnos/editar_turno.html"
    success_url = reverse_lazy("turnos:turnos_recepcion")
    group_required = ['Recepcionista', 'Director', 'Medico']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # NECESARIO
        return kwargs

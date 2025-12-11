# turnos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .models import Turno, Especialidad, ESTADO_TURNO
import mercadopago
from django.conf import settings
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
    

    #MERCADO PAGOOOOOO


def pagar_turno(request, turno_id):
    print("=" * 50)
    print("🚀 ENTRANDO A PAGAR_TURNO")
    print("=" * 50)
    
    turno = get_object_or_404(Turno, id=turno_id)

    token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
    print(f"🔑 TOKEN CONFIGURADO: {token[:20] if token else 'NO CONFIGURADO'}...")
    
    if not token:
        return HttpResponse("ERROR: MERCADOPAGO_ACCESS_TOKEN no está configurado en settings.py")

    try:
        sdk = mercadopago.SDK(token)
        print("✅ SDK inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar SDK: {e}")
        return HttpResponse(f"Error al inicializar Mercado Pago: {e}")

    # Construir URLs completas
    success_url = request.build_absolute_uri(reverse("turnos:confirmar_pago"))
    failure_url = request.build_absolute_uri(reverse("turnos:mis_turnos"))
    
    print(f"✅ SUCCESS URL: {success_url}")
    print(f"✅ FAILURE URL: {failure_url}")
    
    preference_data = {
        "items": [
            {
                "title": f"Pago de turno - {turno.especialidad}",
                "quantity": 1,
                "unit_price": 10000.00,
            }
        ],
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": failure_url,
        },
        # auto_return NO funciona con localhost - comentado
        # "auto_return": "approved",
    }

    print("📦 DATOS ENVIADOS A MERCADO PAGO:")
    print(preference_data)

    try:
        preference = sdk.preference().create(preference_data)
        print("\n🔥 RESPUESTA COMPLETA DE MERCADO PAGO:")
        print(preference)
    except Exception as e:
        print(f"❌ EXCEPCIÓN AL CREAR PREFERENCIA: {e}")
        return HttpResponse(f"Error al crear preferencia: {e}")

    status = preference.get("status")
    response_data = preference.get("response", {})
    
    print(f"\n📊 STATUS: {status}")

    # Intentar obtener init_point
    init_point = None
    preference_id = None

    if status in [200, 201]:
        # Estructura 1: directamente en preference
        init_point = preference.get("init_point")
        preference_id = preference.get("id")
        
        # Estructura 2: dentro de response
        if not init_point and response_data:
            init_point = response_data.get("init_point")
            preference_id = response_data.get("id")

    print(f"\n🎯 INIT POINT ENCONTRADO: {init_point}")
    print(f"🎯 PREFERENCE ID ENCONTRADO: {preference_id}")

    if not init_point:
        error_msg = preference.get("message") or response_data.get("message") or "Error desconocido"
        print(f"\n❌ ERROR FINAL: {error_msg}")
        return HttpResponse(f"Error: {error_msg}")

    turno.id_pago_mp = preference_id
    turno.save()
    print(f"\n✅ REDIRIGIENDO A: {init_point}")

    return redirect(init_point)

def confirmar_pago(request):
    # Capturar los parámetros que envía Mercado Pago
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    preference_id = request.GET.get('preference_id')
    
    print(f"✅ Pago confirmado - Payment ID: {payment_id}, Status: {status}")
    
    # Aquí puedes actualizar el estado del turno
    if preference_id:
        try:
            turno = Turno.objects.get(id_pago_mp=preference_id)
            # turno.estado_pago = 'confirmado'  # Descomenta si tienes este campo
            turno.save()
            return HttpResponse(f"¡Pago confirmado correctamente! ID: {payment_id}")
        except Turno.DoesNotExist:
            return HttpResponse("Turno no encontrado")
    
    return HttpResponse("Pago procesado correctamente.")
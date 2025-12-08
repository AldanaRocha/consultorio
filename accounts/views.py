from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView   # ← ESTA ES LA IMPORTANTE

from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def registro(request):

    # Roles permitidos al director
    roles = Group.objects.all()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Director puede elegir rol
            if request.user.is_superuser or request.user.groups.filter(name="Director").exists():
                rol = request.POST.get("rol")
            else:
                # Otros roles siempre crean PACIENTES
                rol = "Paciente"

            grupo = Group.objects.get(name=rol)
            user.groups.add(grupo)

            messages.success(request, f"Usuario creado como {rol}")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "accounts/registro.html", {
        "form": form,
        "roles": roles
    })

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Obtener el rol elegido desde el formulario
            rol = request.POST.get("rol")

            # Asignar el grupo
            if rol:
                grupo = Group.objects.get(name=rol)
                user.groups.add(grupo)

            login(request, user)
            return redirect("home")  # o página que vos quieras

    else:
        form = UserCreationForm()

    # Pasamos los roles al template
    roles = Group.objects.all()

    return render(request, "registration/registro.html", {
        "form": form,
        "roles": roles
    })

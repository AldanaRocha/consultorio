from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def registro(request):

    # Solo director o superuser pueden elegir rol
    if request.user.is_superuser or request.user.groups.filter(name="Director").exists():
        roles = Group.objects.all()
    else:
        # Para que el usuario común NO pueda crear directores o médicos
        roles = Group.objects.filter(name="Paciente")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Si NO es director o admin → siempre crea PACIENTES
            if request.user.is_superuser or request.user.groups.filter(name="Director").exists():
                rol = request.POST.get("rol")
            else:
                rol = "Paciente"

            grupo = Group.objects.get(name=rol)
            user.groups.add(grupo)

            messages.success(request, f"Usuario creado como {rol}")
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "registration/registro.html", {
        "form": form,
        "roles": roles
    })

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

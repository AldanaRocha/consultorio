from django.shortcuts import render, redirect, get_object_or_404
from .models import Especialidad
from .forms import EspecialidadForm
from django.contrib.auth.decorators import login_required


@login_required
def especialidad_lista(request):
    especialidades = Especialidad.objects.all()
    return render(request, "especialidades/lista.html", {
        "especialidades": especialidades
    })


@login_required
def especialidad_crear(request):
    if request.method == "POST":
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("especialidades:lista_especialidades")
    else:
        form = EspecialidadForm()

    return render(request, "especialidades/crear.html", {
        "form": form
    })


@login_required
def especialidad_editar(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)

    if request.method == "POST":
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            return redirect("especialidades:lista_especialidades")
    else:
        form = EspecialidadForm(instance=especialidad)

    return render(request, "especialidades/editar.html", {
        "form": form
    })

@login_required
def especialidad_eliminar(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)

    if request.method == "POST":
        # borrar y volver a la lista
        especialidad.delete()
        return redirect("especialidades:lista_especialidades")

    # Si es GET mostramos página de confirmación
    return render(request, "especialidades/eliminar.html", {
        "especialidad": especialidad
    })

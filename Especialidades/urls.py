from django.urls import path
from . import views


app_name = "especialidades"



urlpatterns = [
    path("", views.especialidad_lista, name="lista_especialidades"),

    path("crear/", views.especialidad_crear, name="crear_especialidad"),

    path("editar/<int:pk>/", views.especialidad_editar, name="editar_especialidad"),

    path("eliminar/<int:pk>/", views.especialidad_eliminar, name="eliminar_especialidad"),


    
]

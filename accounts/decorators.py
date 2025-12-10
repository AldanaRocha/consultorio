from django.contrib.auth.decorators import user_passes_test

def grupo_requerido(nombre_grupo):
    return user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name=nombre_grupo).exists(),
        login_url='/accounts/login/'
    )

director_required = grupo_requerido("Director")
medico_required = grupo_requerido("Medico")
recepcionista_required = grupo_requerido("Recepcionista")
paciente_required = grupo_requerido("Paciente")

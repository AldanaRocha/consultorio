from django.contrib import admin
from django.urls import path, include
from turnos import views as turnos_views

urlpatterns = [
    path('', turnos_views.home, name='home'),

    path('turnos/', include(('turnos.urls', 'turnos'), namespace='turnos')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('esp/', include('Especialidades.urls')),

    path('admin/', admin.site.urls),
]

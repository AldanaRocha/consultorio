from django.contrib import admin
from django.urls import path, include
from turnos.views import home_redirect

urlpatterns = [
    path('', include('turnos.urls')),   
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # << AGREGADO
    path('', include('turnos.urls')),
    path('admin/', admin.site.urls),
]

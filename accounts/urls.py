from django.urls import path
from .views import CustomLoginView, registro

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("registro/", registro, name="registro"),
]

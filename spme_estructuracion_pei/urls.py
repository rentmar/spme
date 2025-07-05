from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'crearEstructuracionPEI/',views.CrearEstructuraPEI.as_view(), name='crearEstructuracionPEI'),
    path(r'obtenerEstructuracionPEI/',views.ObtenerEstructuraPEI.as_view(), name='obtenerEstructuracionPEI'),
]
urlpatterns += router.urls
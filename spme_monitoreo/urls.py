from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'crearSolicitudFondos/',views.SolicitudFondos.as_view(), name='crearSolicitudFondos'),
    path(r'crearRendicionCuentas/',views.RendicionCuentas.as_view(), name='crearRendicionCuentas'),
    path(r'crearSolicitudReembolso/',views.SolicitudReembolso.as_view(), name='crearSolicitudReembolso'),
    path(r'crearSolicitudViaje/',views.SolicitudViaje.as_view(), name='crearSolicitudViaje'),
    path(r'crearSolicitudPagoDirecto/',views.SolicitudPagoDirecto.as_view(), name='crearSolicitudPagoDirecto'),
    path(r'obtenerDatosFormulario/', views.ObtenerDatosFormulario.as_view(), name='obtenerDatosFormulario'),
]
urlpatterns += router.urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'crearSolicitudFondos/',views.SolicitudFondos.as_view(), name='crearSolicitudFondos'),
    path(r'obtenerSolicitudFondos/',views.ObtenerSolicitudFondos.as_view(), name='obtenerSolicitudFondos'),
    path(r'obtener-solicitudFondosPor-idAidUidT/', views.ObtenerSolicitudFondosPorFiltros.as_view(), name='obtener-solicitudFondosPor-idAidUidT'),
    path(r'crearRendicionCuentas/',views.RendicionCuentas.as_view(), name='crearRendicionCuentas'),
    path(r'crearSolicitudReembolso/',views.SolicitudReembolso.as_view(), name='crearSolicitudReembolso'),
    path(r'crearSolicitudViaje/',views.SolicitudViaje.as_view(), name='crearSolicitudViaje'),
    path(r'crearSolicitudPagoDirecto/',views.SolicitudPagoDirecto.as_view(), name='crearSolicitudPagoDirecto'),
    path(r'obtenerDatosFormulario/', views.ObtenerDatosFormulario.as_view(), name='obtenerDatosFormulario'),
    path('actualizar-validacion-solicitud-fondos/', views.ActualizarValidacionSolicitudFondos.as_view(), name='actualizar_validacion_solicitud_fondos'),
    path(r'obtenerRendicionDeCuentas/',views.ObtenerRendicionDeCuentas.as_view(), name='obtenerRendicionDeCuentas'),
    path(r'actualizar-validacion-rendicion-cuentas/', views.ActualizarValidacionRendicionCuentas.as_view(), name='actualizar_validacion_rendicion_cuentas'),
]
urlpatterns += router.urls
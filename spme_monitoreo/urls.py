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
    path(r'obtenerSolicitudReembolso/',views.ObtenerSolicitudReembolso.as_view(), name='obtenerSolicitudReembolso'),
    path(r'actualizar-validacion-solicitud-reembolso/', views.ActualizarValidacionSolicitudReembolso.as_view(), name='actualizar_validacion_solicitud_reembolso'),
    path(r'obtenerFormasPago/', views.ObtenerFormasPago.as_view(), name='obtenerFormasPago'),
    path(r'diagnosticarSolicitudViaje/', views.DiagnosticarSolicitudViaje.as_view(), name='diagnosticarSolicitudViaje'),
    path(r'obtenerSolicitudesViaje/', views.ObtenerSolicitudesViaje.as_view(), name='obtenerSolicitudesViaje'),
    path(r'actualizar-validacion-solicitud-viaje/', views.ActualizarValidacionSolicitudViaje.as_view(), name='actualizar_validacion_solicitud_viaje'),
    path(r'obtenerSolicitudesPagoDirecto/', views.ObtenerSolicitudesPagoDirecto.as_view(), name='obtenerSolicitudesPagoDirecto'),
    path(r'actualizar-validacion-solicitud-pago-directo/', views.ActualizarValidacionSolicitudPagoDirecto.as_view(), name='actualizar_validacion_solicitud_pago_directo'),
]
urlpatterns += router.urls
# spme/spme_validaciones/urls.py
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.validaciones_informes_actividad_subac_views import (
    ValidacionViewSet,
    AsignarValidadoresViewSet,
    EstadoValidacionViewSet,
    ResetearValidacionesViewSet,
    EstadoValidacionInformeAPIView,
    EstadoValidacionInformeTareaAPIView,
)
from .views.obtener_lista_validadores_views import UsuarioValidacionAPIView

#Importaciones para solicitud de fondos
from .views.validaciones_solicitud_fondos_views import (
    AsignarValidadoresSolicitudFondosViewSet,
    VotarSolicitudFondosViewSet,
    ResetearValidacionesSolicitudFondosViewSet,
    EstadoValidacionSolicitudFondosAPIView,
    HistorialValidacionSolicitudFondosAPIView,
    MisValidacionesPendientesSolicitudFondosAPIView,
    AsignarValidadoresSolicitudFondosSinNotificacionViewSet,
    ListarRevisoresSolicitudFondosAPIView,
    ActualizarRevisoresSolicitudFondosAPIView,
)

#Importaciones para solicitud de viajes
from .views.validaciones_solicitud_viaje_views import(
    AsignarValidadoresSolicitudViajeViewSet,
    VotarSolicitudViajeViewSet,
    EstadoValidacionSolicitudViajeAPIView,
    ResetearValidacionesSolicitudViajeViewSet,
    HistorialValidacionSolicitudViajeAPIView,
    MisValidacionesPendientesSolicitudViajeAPIView,
    AsignarValidadoresSolicitudViajeSinNotificacionViewSet,
)

#Importaciones para Sol de pago directo
from .views.validaciones_solicitud_pago_directo_views import (
    AsignarValidadoresSolicitudPagoDirectoViewSet,
    VotarSolicitudPagoDirectoViewSet,
    EstadoValidacionSolicitudPagoDirectoAPIView,
    ResetearValidacionesSolicitudPagoDirectoViewSet,
    HistorialValidacionSolicitudPagoDirectoAPIView,
    MisValidacionesPendientesSolicitudPagoDirectoAPIView,
    AsignarValidadoresSolicitudPagoDirectoSinNotificacionViewSet,
)

#Importaciones para Sol de reembolso
from .views.validaciones_solicitud_reembolso_views import (
    AsignarValidadoresSolicitudReembolsoViewSet,
    VotarSolicitudReembolsoViewSet,
    EstadoValidacionSolicitudReembolsoAPIView,
    ResetearValidacionesSolicitudReembolsoViewSet,
    HistorialValidacionSolicitudReembolsoAPIView,
    MisValidacionesPendientesSolicitudReembolsoAPIView,
    AsignarValidadoresSolicitudReembolsoSinNotificacionViewSet,
)

# Importaciones para rendición de cuentas
from .views.validaciones_rendicion_cuentas_views import (
    AsignarValidadoresRendicionCuentasViewSet,
    VotarRendicionCuentasViewSet,
    ResetearValidacionesRendicionCuentasViewSet,
    EstadoValidacionRendicionCuentasAPIView,
    HistorialValidacionRendicionCuentasAPIView,
    MisValidacionesPendientesRendicionCuentasAPIView,
    AsignarValidadoresRendicionCuentasSinNotificacionViewSet,
)

#Importacion para solicitudes y rendicion
from .views.todas_solicitudes_usuario_views import (
    TodasSolicitudesUsuarioView, 
    TodasSolicitudesPendientesUsuarioView,
    TodasValidacionesUsuarioView
)
from .views.solicitudes_fondos_usuario_views import SolicitudesFondosUsuarioView
from .views.solicitudes_viaje_usuario_views import SolicitudesViajeUsuarioView
from .views.solicitudes_pago_directo_usuario_views import SolicitudesPagoDirectoUsuarioView
from .views.solicitudes_reembolso_usuario_views import SolicitudesReembolsoUsuarioView
from .views.rendicion_cuentas_usuario_views import RendicionCuentasUsuarioView

router = DefaultRouter()

#Validadores Informes Actividad/Tarea
router.register(r'validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    ################################# Validacion de Informes ###################################################
    #Validadores Informes Actividad/Tarea
    path(r'asignar-validadores/', AsignarValidadoresViewSet.as_view({'post': 'create'}), name='asignar-validadores'),
    path(r'estado-validacion/', EstadoValidacionViewSet.as_view({'get': 'list'}), name='estado-validacion'),
    path(r'resetear-validaciones/', ResetearValidacionesViewSet.as_view({'post': 'create'}), name='resetear-validaciones'),
    #Obtener redactor y validadores
    path(r'lista-usuario-redactor-validadores/', UsuarioValidacionAPIView.as_view(), name='lista_usuario_redactor_con_validadores'),
    #Endpoint para verificar el estado de validacion de un Informe de Actividad Principal
    path(r'informe-actividad/<int:informe_id>/estado-validacion/', EstadoValidacionInformeAPIView.as_view(), name='estado-validacion-informe-principal'),
    # Endpoint para verificar estado de validación de un informe de tarea específico
    path(r'informe-tarea/<int:informe_id>/estado-validacion/', EstadoValidacionInformeTareaAPIView.as_view(), name='estado-validacion-informe-tarea-principal'),

    ################################ Validaciones de Solicitud de Fondos ######################################################
    path(r'solicitud-fondos/<int:solicitud_id>/asignar-validadores/', AsignarValidadoresSolicitudFondosViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-fondos'),
    path(r'solicitud-fondos/<int:solicitud_id>/votar/', VotarSolicitudFondosViewSet.as_view({'post': 'create'}), name='votar-solicitud-fondos'),
    path(r'solicitud-fondos/<int:solicitud_id>/estado-validacion/', EstadoValidacionSolicitudFondosAPIView.as_view(), name='estado-validacion-solicitud-fondos'),
    path(r'solicitud-fondos/<int:solicitud_id>/resetear-validaciones/', ResetearValidacionesSolicitudFondosViewSet.as_view({'post': 'create'}), name='resetear-validaciones-solicitud-fondos'),
    path(r'solicitud-fondos/<int:solicitud_id>/historial/', HistorialValidacionSolicitudFondosAPIView.as_view(), name='historial-solicitud-fondos'),
    path(r'solicitud-fondos/mis-pendientes/', MisValidacionesPendientesSolicitudFondosAPIView.as_view(), name='mis-pendientes-solicitud-fondos'),
    path(r'solicitud-fondos/<int:solicitud_id>/asignar-validadores-sin-notificacion/', AsignarValidadoresSolicitudFondosSinNotificacionViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-fondos-sin-notificacion'),
    path(r'solicitud-fondos/<int:solicitud_id>/revisores/', ListarRevisoresSolicitudFondosAPIView.as_view(), name='listar-revisores-solicitud-fondos' ),
    path(r'solicitud-fondos/<int:solicitud_id>/revisores/actualizar/', ActualizarRevisoresSolicitudFondosAPIView.as_view(), name='actualizar-revisores-solicitud-fondos' ),
    ################################ Validaciones de Solicitud de Viajes ######################################################
    path(r'solicitud-viajes/<int:solicitud_id>/asignar-validadores/', AsignarValidadoresSolicitudViajeViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-viaje'),
    path(r'solicitud-viajes/<int:solicitud_id>/votar/', VotarSolicitudViajeViewSet.as_view({'post': 'create'}), name='votar-solicitud-viaje'),
    path(r'solicitud-viajes/<int:solicitud_id>/estado-validacion/', EstadoValidacionSolicitudViajeAPIView.as_view(), name='estado-validacion-solicitud-viaje'),
    path(r'solicitud-viajes/<int:solicitud_id>/resetear-validaciones/', ResetearValidacionesSolicitudViajeViewSet.as_view({'post': 'create'}), name='resetear-validaciones-solicitud-viaje'),
    path(r'solicitud-viajes/<int:solicitud_id>/historial/', HistorialValidacionSolicitudViajeAPIView.as_view(), name='historial-solicitud-viaje'),
    path(r'solicitud-viajes/mis-pendientes/', MisValidacionesPendientesSolicitudViajeAPIView.as_view(), name='mis-pendientes-solicitud-viaje'),
    path(r'solicitud-viajes/<int:solicitud_id>/asignar-validadores-sin-notificacion/', AsignarValidadoresSolicitudViajeSinNotificacionViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-viaje-sin-notificacion'),
    ################################ Validaciones de Solicitud de Pago Directo ##############################################
    path(r'solicitud-pago-directo/<int:solicitud_id>/asignar-validadores/', AsignarValidadoresSolicitudPagoDirectoViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/<int:solicitud_id>/votar/', VotarSolicitudPagoDirectoViewSet.as_view({'post': 'create'}), name='votar-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/<int:solicitud_id>/estado-validacion/', EstadoValidacionSolicitudPagoDirectoAPIView.as_view(), name='estado-validacion-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/<int:solicitud_id>/resetear-validaciones/', ResetearValidacionesSolicitudPagoDirectoViewSet.as_view({'post': 'create'}), name='resetear-validaciones-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/<int:solicitud_id>/historial/', HistorialValidacionSolicitudPagoDirectoAPIView.as_view(), name='historial-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/mis-pendientes/', MisValidacionesPendientesSolicitudPagoDirectoAPIView.as_view(), name='mis-pendientes-solicitud-pago-directo'),
    path(r'solicitud-pago-directo/<int:solicitud_id>/asignar-validadores-sin-notificacion/', AsignarValidadoresSolicitudPagoDirectoSinNotificacionViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-pago-directo-sin-notificacion'),
    ################################ Validaciones de Solicitud de Reembolso ##############################################
    path(r'solicitud-reembolso/<int:solicitud_id>/asignar-validadores/', AsignarValidadoresSolicitudReembolsoViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-reembolso'),
    path(r'solicitud-reembolso/<int:solicitud_id>/votar/', VotarSolicitudReembolsoViewSet.as_view({'post': 'create'}), name='votar-solicitud-reembolso'),
    path(r'solicitud-reembolso/<int:solicitud_id>/estado-validacion/', EstadoValidacionSolicitudReembolsoAPIView.as_view(), name='estado-validacion-solicitud-reembolso'),
    path(r'solicitud-reembolso/<int:solicitud_id>/resetear-validaciones/', ResetearValidacionesSolicitudReembolsoViewSet.as_view({'post': 'create'}), name='resetear-validaciones-solicitud-reembolso'),
    path(r'solicitud-reembolso/<int:solicitud_id>/historial/', HistorialValidacionSolicitudReembolsoAPIView.as_view(), name='historial-solicitud-reembolso'),
    path(r'solicitud-reembolso/mis-pendientes/', MisValidacionesPendientesSolicitudReembolsoAPIView.as_view(), name='mis-pendientes-solicitud-reembolso'),
    path(r'solicitud-reembolso/<int:solicitud_id>/asignar-validadores-sin-notificacion/', AsignarValidadoresSolicitudReembolsoSinNotificacionViewSet.as_view({'post': 'create'}), name='asignar-validadores-solicitud-reembolso-sin-notificacion'),
    ################################ Validaciones de Rendición de Cuentas ##############################################
    path(r'rendicion-cuentas/<int:rendicion_id>/asignar-validadores/', AsignarValidadoresRendicionCuentasViewSet.as_view({'post': 'create'}), name='asignar-validadores-rendicion-cuentas'),
    path(r'rendicion-cuentas/<int:rendicion_id>/votar/', VotarRendicionCuentasViewSet.as_view({'post': 'create'}), name='votar-rendicion-cuentas'),
    path(r'rendicion-cuentas/<int:rendicion_id>/estado-validacion/', EstadoValidacionRendicionCuentasAPIView.as_view(), name='estado-validacion-rendicion-cuentas'),
    path(r'rendicion-cuentas/<int:rendicion_id>/resetear-validaciones/', ResetearValidacionesRendicionCuentasViewSet.as_view({'post': 'create'}), name='resetear-validaciones-rendicion-cuentas'),
    path(r'rendicion-cuentas/<int:rendicion_id>/historial/', HistorialValidacionRendicionCuentasAPIView.as_view(), name='historial-rendicion-cuentas'),
    path(r'rendicion-cuentas/mis-pendientes/', MisValidacionesPendientesRendicionCuentasAPIView.as_view(), name='mis-pendientes-rendicion-cuentas'),
    path(r'rendicion-cuentas/<int:rendicion_id>/asignar-validadores-sin-notificacion/', AsignarValidadoresRendicionCuentasSinNotificacionViewSet.as_view({'post': 'create'}), name='asignar-validadores-rendicion-cuentas-sin-notificacion'),
    ############################### Listas de Solicitudes validadas/no validadas #############
    path(r'mis-solicitudes/', TodasSolicitudesUsuarioView.as_view(), name='todas-mis-solicitudes'),
    path(r'mis-solicitudes-pendientes/', TodasSolicitudesPendientesUsuarioView.as_view(), name='todas-mis-solicitudes-pendientes'),
    path(r'mis-solicitudes-revisor/',TodasValidacionesUsuarioView.as_view(), name='solicitudes_usuario_revisor'),
    path(r'mis-solicitudes-fondos/', SolicitudesFondosUsuarioView.as_view(), name='solicitudes-fondos-usuario'),
    path(r'mis-solicitudes-viaje/', SolicitudesViajeUsuarioView.as_view(), name='solicitudes-viaje-usuario'),
    path(r'mis-solicitudes-pago-directo/', SolicitudesPagoDirectoUsuarioView.as_view(), name='solicitudes-pago-directo-usuario'),
    path(r'mis-solicitudes-reembolso/', SolicitudesReembolsoUsuarioView.as_view(), name='solicitudes-reembolso-usuario'),
    path(r'mis-rendiciones-cuentas/', RendicionCuentasUsuarioView.as_view(), name='rendicion-cuentas-usuario'),
]  

urlpatterns += router.urls
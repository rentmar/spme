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
)


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
] 

urlpatterns += router.urls
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
    
] 

urlpatterns += router.urls
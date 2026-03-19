from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.validaciones_informes_actividad_subac_views import (
    ValidacionViewSet,
    AsignarValidadoresViewSet,
    EstadoValidacionViewSet,
    ResetearValidacionesViewSet,
)
from .views.obtener_lista_validadores_views import UsuarioValidacionAPIView

router = DefaultRouter()

#Validadores Informes Actividad/Tarea
router.register(r'validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    #Validadores Informes Actividad/Tarea
    path(r'asignar-validadores/', AsignarValidadoresViewSet.as_view({'post': 'create'}), name='asignar-validadores'),
    path(r'estado-validacion/', EstadoValidacionViewSet.as_view({'get': 'list'}), name='estado-validacion'),
    path(r'resetear-validaciones/', ResetearValidacionesViewSet.as_view({'post': 'create'}), name='resetear-validaciones'),
    #Obtener redactor y validadores
    path(r'lista-usuario-redactor-validadores/', UsuarioValidacionAPIView.as_view(), name='lista_usuario_redactor_con_validadores'),

] 

urlpatterns += router.urls
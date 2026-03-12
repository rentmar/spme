from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.validaciones_informes_actividad_subac_views import (
    ValidacionViewSet,
    AsignarValidadoresViewSet,
    EstadoValidacionViewSet,
    ResetearValidacionesViewSet,
)

router = DefaultRouter()

router.register(r'validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    #Test de conexion
    path(r'asignar-validadores/', AsignarValidadoresViewSet.as_view({'post': 'create'}), name='asignar-validadores'),
    path(r'estado-validacion/', EstadoValidacionViewSet.as_view({'get': 'list'}), name='estado-validacion'),
    path(r'resetear-validaciones/', ResetearValidacionesViewSet.as_view({'post': 'create'}), name='resetear-validaciones'),

] 

urlpatterns += router.urls
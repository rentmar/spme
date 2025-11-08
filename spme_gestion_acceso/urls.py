from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.test_views import TestConnectionView
from .views.permisos_views import (
    obtener_permisos_usuario,
    verificar_acceso_proyecto,
    lista_proyectos_accesibles
)
from .views.usuario_instancia_views import UserInstanciaGestoraViewSet, PermisoProyectoEspecificoViewSet

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'programas', ProgramaViewset, basename='programas-areas')
router.register(r'user-instancias', UserInstanciaGestoraViewSet, basename='userinstancia')
router.register(r'permisos-especificos', PermisoProyectoEspecificoViewSet, basename='permisoespecifico')

urlpatterns = [
    #path(r'programa/test/', test_endpoint, name='test_endpoint'), 
    path(r'test/gestion-acceso/', TestConnectionView.as_view(), name='test-gestion-acceso'),
    #Endpoint de permisos
    path(r'permisos/usuario/', obtener_permisos_usuario, name='obtener_permisos_usuario'),
    path(r'permisos/verificar-acceso/<int:proyecto_id>/', verificar_acceso_proyecto, name='verificar_acceso_proyecto'),
    path(r'permisos/proyectos/', lista_proyectos_accesibles, name='lista_proyectos_accesibles'),
    #Endpoints adicionales
    path(r'api/user-instancias/mis-instancias/', UserInstanciaGestoraViewSet.as_view({'get': 'mis_instancias'}), name='mis_instancias'),
    path(r'api/permisos-especificos/mis-permisos/', PermisoProyectoEspecificoViewSet.as_view({'get': 'mis_permisos_especificos'}), name='mis_permisos_especificos'),

]

urlpatterns += router.urls
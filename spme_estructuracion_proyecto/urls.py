from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.proyecto_detalle_views import test_connection, ProyectoDetailView
from .views.actualizar_estructura_views import actualizar_estructura_diagrama

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')

urlpatterns = [

    path(r'proyectos/test-conexion/', test_connection, name='proyecto-test'),
    path(r'proyectos/<int:id>/detalles/', ProyectoDetailView.as_view(), name='proyecto_detalles_por_id' ),
    #path(r'actualizar-estructura/', actualizar_estructura_completa, name='actualizar_estructura'),
    path(r'proyectos/diagrama/<int:diagrama_id>/actualizar-estructura/', actualizar_estructura_diagrama, name='actualizar_estructura_transaccional' ),

] 

urlpatterns += router.urls
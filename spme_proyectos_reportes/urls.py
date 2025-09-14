from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.estructura_jerarquica_proy_views import prueba_conexion_reportes, estructura_jerarquica_completa
from .views.crear_entrada_bitacora_indicador_view import BitacoraIndicadorViewSet
from .views.test_docx_view import test_docx_status, test_docx_endpoint


router = DefaultRouter()

router.register(r'bitacora-indicadores', BitacoraIndicadorViewSet, basename='bitacora_indicador')
#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')

urlpatterns = [
    path(r'test-cnx/', prueba_conexion_reportes, name='reportes-test'),
    path(r'proyecto/estructura-jerarquica/<int:proyecto_id>/', estructura_jerarquica_completa, name='proyecto_estruc_jerarquica'),
    #enpoint de prueba
    path(r'test/docx/generate/', test_docx_endpoint, name='test-docx-generate'),
    path(r'test/docx/status/', test_docx_status, name='test-docx-status'),

    #path(r'proyectos/test-conexion/', test_connection, name='proyecto-test'),
    #path(r'proyectos/<int:id>/detalles/', ProyectoDetailView.as_view(), name='proyecto_detalles_por_id' ),
    #path(r'actualizar-estructura/', actualizar_estructura_completa, name='actualizar_estructura'),
    #path(r'proyectos/diagrama/<int:diagrama_id>/actualizar-estructura/', actualizar_estructura_diagrama, name='actualizar_estructura_transaccional' ),


] 

urlpatterns += router.urls
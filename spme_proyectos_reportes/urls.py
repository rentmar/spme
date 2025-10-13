from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.estructura_jerarquica_proy_views import prueba_conexion_reportes, estructura_jerarquica_completa
from .views.test_docx_view import test_docx_status, test_docx_endpoint
from .views.reporte_actividad_view import generar_reporte_actividad, info_reporte_actividad
from .views.estructura_proyecto_reportes_views import ProyectoEstructuraCompletaView
from .views.proyecto_reporte_view import ProyectoReporteCompletoView, descargar_reporte_proyecto
from .views.crear_rep_actividad_tareas_views import generar_reporte_actividad_word
#from .views.get_bitacora_id_tipo_views import bitacoras_por_indicador
from .views.proyectos_report_views import ProyectoReportAllView
from .views.reporte_proyecto_view import ReporteProyectoViewSet

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'bitacora-indicador', BitacoraIndicadorViews, basename='bitacora_indicadores_views')

urlpatterns = [
    path(r'test-cnx/', prueba_conexion_reportes, name='reportes-test'),
    path(r'proyecto/estructura-jerarquica/<int:proyecto_id>/', estructura_jerarquica_completa, name='proyecto_estruc_jerarquica'),
    #enpoint de prueba
    path(r'test/docx/generate/', test_docx_endpoint, name='test-docx-generate'),
    path(r'test/docx/status/', test_docx_status, name='test-docx-status'),
    path(r'proyectos/<int:id>/estructura-reportes/', ProyectoEstructuraCompletaView.as_view(), name='proyecto_estrucuctura_completa_reportes' ),
    #Registro de bitacoras
    #path(r'bitacora-indicador/crear/', crear_bitacora_indicador, name='crear-bitacora-indicador' ),
    #path(r'bitacora-indicador/obtener/', obtener_bitacoras_indicador, name='obtener_bitacoras_indicador'),
    #path(r'bitacora-indicador/obtener-detallado/', obtener_bitacoras_indicador_detallado, name='obtener_bitacoras_indicador_detallado'),
    #path(r'bitacoras-lista-tipo-id/', bitacoras_por_indicador, name='bitacoras-por-indicador' ),
    #Reporte de proyecto
    path(r'proyectos/<int:id>/reporte-completo/', ProyectoReporteCompletoView.as_view(), name='proyecto-reporte-completo'),
    path(r'proyectos/<int:id>/descargar-reporte/', descargar_reporte_proyecto, name='descargar-reporte-proyecto'),
    #Reporte de Acividades
    path(r'actividades/<int:actividad_id>/reporte/generar/', generar_reporte_actividad, name='generar-reporte-actividad'),
    path(r'actividades/<int:actividad_id>/reporte/info/', info_reporte_actividad, name='info-reporte-actividad'),
    path(r'actividad/<int:actividad_id>/reporte-word/', generar_reporte_actividad_word, name='actividad_tarea_reporte'),
    #path(r'proyectos/test-conexion/', test_connection, name='proyecto-test'),
    #path(r'proyectos/<int:id>/detalles/', ProyectoDetailView.as_view(), name='proyecto_detalles_por_id' ),
    #path(r'actualizar-estructura/', actualizar_estructura_completa, name='actualizar_estructura'),
    #path(r'proyectos/diagrama/<int:diagrama_id>/actualizar-estructura/', actualizar_estructura_diagrama, name='actualizar_estructura_transaccional' ),
    path(r'proyecto-reporte-rapido/<int:proyecto_id>/word/',  ProyectoReportAllView.as_view(), name='proyecto-reporte-descargar'),

] 

urlpatterns += router.urls
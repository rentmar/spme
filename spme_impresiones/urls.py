from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.test_conexion import TestConexionView
from .views.generar_solicitudes_pdf_views import ReportesViewSet

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'bitacora-indicador', BitacoraIndicadorViews, basename='bitacora_indicadores_views')

urlpatterns = [
    #Test de conexion
    path(r'test-cnx-impresiones/', TestConexionView.as_view(), name='impresiones-test'),
    ########################## Solicitudes Proyectos #####################################
    path(r'solicitud-fondos/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_fondos'}), name='solicitud_fondos_pdf'),
    path(r'solicitud-reposicion/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_reembolso'}), name='solicitud_reembolso_pdf'),
    path(r'solicitud-viaje/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_viaje'}), name='solicitud_viaje_pdf'),
    path(r'solicitud-pago-directo/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_pago_directo'}), name='solicitud_pago_directo_pdf'),
    path(r'rendicion-cuentas/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'rendicion_cuentas'}), name='rendicion_cuentas_pdf'),
    path(r'solicitud-fondos-tarea/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_fondos_tarea'}), name='solicitud_fondos_tarea_pdf'),
    path(r'solicitud-reposicion-tarea/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_reembolso_tarea'}), name='solicitud_reembolso_tarea_pdf' ),
    path(r'solicitud-viaje-tarea/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_viaje_tarea'}), name='solicitud_viaje_tarea_pdf'),
    path(r'solicitud-pago-directo-tarea/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_pago_directo_tarea'}), name='solicitud_pago_directo_tarea_pdf'),
    path(r'rendicion-cuentas-tareas/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'rendicion_cuentas_tarea'}), name='rendicion_cuentas_tareas_pdf'),
    path(r'solicitud-fondos-actividad-pei/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_fondos_actividad_pei'}),  name='solicitud_fondos_actividad_pei_pdf' ),
    path(r'solicitud-fondos-tarea-pei/<int:pk>/pdf/', ReportesViewSet.as_view({'get': 'solicitud_fondos_tarea_pei'}), name='solicitud_fondos_tarea_pei_pdf'),


] 

urlpatterns += router.urls
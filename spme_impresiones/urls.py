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
    path(r'solicitud-fondos/<int:pk>/pdf/',
         ReportesViewSet.as_view({'get': 'solicitud_fondos'}),
         name='solicitud_fondos_pdf'),
    path(r'solicitud-reembolso/<int:pk>/pdf/',
         ReportesViewSet.as_view({'get': 'solicitud_reembolso'}),
         name='solicitud_reembolso_pdf'),
    
    path(r'solicitud-viaje/<int:pk>/pdf/',
         ReportesViewSet.as_view({'get': 'solicitud_viaje'}),
         name='solicitud_viaje_pdf'),
    
    path(r'solicitud-pago-directo/<int:pk>/pdf/',
         ReportesViewSet.as_view({'get': 'solicitud_pago_directo'}),
         name='solicitud_pago_directo_pdf'),
    
    path(r'rendicion-cuentas/<int:pk>/pdf/',
         ReportesViewSet.as_view({'get': 'rendicion_cuentas'}),
         name='rendicion_cuentas_pdf'),
] 

urlpatterns += router.urls
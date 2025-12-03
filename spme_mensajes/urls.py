from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.test_conexion import TestConexionView

from .views.views_correos_especificos import (
    prueba_correo_prueba, 
    prueba_correo_pendiente,
    prueba_correo_aprobada,
    ejemplos_datos,
    )



router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'bitacora-indicador', BitacoraIndicadorViews, basename='bitacora_indicadores_views')

urlpatterns = [
    #Test de conexion
    path(r'test-cnx-mensajes/', TestConexionView.as_view(), name='mensajes-test'),
    path(r'correos/prueba-sistema/', prueba_correo_prueba, name='prueba_correo_prueba'),
    path(r'correos/solicitud-pendiente/', prueba_correo_pendiente, name='prueba_correo_pendiente'),
    path(r'correos/solicitud-aprobada/', prueba_correo_aprobada, name='prueba_correo_aprobada'),
    path(r'correos/ejemplos/', ejemplos_datos, name='ejemplos_datos'),
] 

urlpatterns += router.urls
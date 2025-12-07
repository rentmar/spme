from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.test_conexion import TestConexionView
#correos
from .views.views_correos_especificos import (
    prueba_correo_prueba, 
    prueba_correo_pendiente,
    prueba_correo_aprobada,
    ejemplos_datos,
    )

#mensajes
from .views.mensaje_views import(
    obtener_bandeja_entrada,
    obtener_mensaje,
    crear_mensaje_privado,
    actualizar_estado_mensaje,
    marcar_varios_leido,
    marcar_todos_leido,
    buscar_mensajes,
    obtener_estadisticas,
    enviar_alerta_actividad,
    obtener_mensajes_actividad,
    obtener_mensajes_proyecto,
    obtener_ejemplos,
    enviar_mensaje_prueba,
)
#Mensajes
from .views.mensajeria_views import (
    CrearMensajeView,
    CrearMensajeSistemaView,
    CrearMensajeMultipleView,
)

from .views.mensaje_automatico_sistema_views import CrearMensajeAutomaticoSistemaView



router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'bitacora-indicador', BitacoraIndicadorViews, basename='bitacora_indicadores_views')

urlpatterns = [
    #Test de conexion
    path(r'test-cnx-mensajes/', TestConexionView.as_view(), name='mensajes-test'),
    ########################## Correos ##########################
    path(r'correos/prueba-sistema/', prueba_correo_prueba, name='prueba_correo_prueba'),
    path(r'correos/solicitud-pendiente/', prueba_correo_pendiente, name='prueba_correo_pendiente'),
    path(r'correos/solicitud-aprobada/', prueba_correo_aprobada, name='prueba_correo_aprobada'),
    path(r'correos/ejemplos/', ejemplos_datos, name='ejemplos_datos'),
    ######################### Mensajeria ##########################
    #bandeja
    path(r'mensajes/bandeja/', obtener_bandeja_entrada, name='obtener_bandeja'),
    #Mensajes individuales
    path(r'mensajes/<int:mensaje_id>/', obtener_mensaje, name='obtener_mensaje'),
    path(r'mensajes/enviar/', crear_mensaje_privado, name='enviar_mensaje'),
    path(r'mensajes/<int:mensaje_id>/estado/', actualizar_estado_mensaje, name='actualizar_estado'),
    #Operaciones masivas
    path(r'marcar-leidos/', marcar_varios_leido, name='marcar_varios_leido'),
    path(r'marcar-todos-leidos/', marcar_todos_leido, name='marcar_todos_leido'),
    #busqueda y estadistica
    path(r'mensajes/buscar/', buscar_mensajes, name='buscar_mensajes'),
    path(r'mensajes/estadisticas/', obtener_estadisticas, name='obtener_estadisticas'),
    #Integracion con actividades
    path(r'mensajes/alertas/actividad/', enviar_alerta_actividad, name='alerta_actividad'),
    path(r'mensajes/actividad/<int:actividad_id>/', obtener_mensajes_actividad, name='mensajes_actividad'),
    path(r'mensajes/proyecto/<int:proyecto_id>/', obtener_mensajes_proyecto, name='mensajes_proyecto'),
    #Pruebas y ejemplos
    path(r'mensajes/ejemplos/', obtener_ejemplos, name='ejemplos'),
    path(r'prueba/', enviar_mensaje_prueba, name='enviar_prueba'),
    #mensajes
    path(r'mensajes/crear/', CrearMensajeView.as_view(), name='crear_mensaje'),
    path(r'mensajes/crear/sistema/', CrearMensajeSistemaView.as_view(), name='crear_mensaje_sistema'),
    path(r'mensajes/crear/multiple/', CrearMensajeMultipleView.as_view(), name='crear_mensaje_multiple'),
    path(r'mensajes/crear/sistema-automatico/', CrearMensajeAutomaticoSistemaView.as_view(), name='crear_mensaje_sistema_automatico'),
    
] 

urlpatterns += router.urls
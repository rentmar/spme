from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.test_conexion import TestConexionView
#correos
from .views.views_correos_especificos import (
    prueba_correo_prueba, 
    prueba_correo_pendiente,
    prueba_correo_aprobada,
    prueba_correo_nuevo_mensaje,
    ejemplos_datos,
    )

#mensajes
from .views.mensaje_views import(
    obtener_bandeja_entrada,
    obtener_mensaje,
    crear_mensaje_privado,
    crear_mensaje_multiple,
    actualizar_estado_mensaje,
    marcar_varios_leido,
    marcar_todos_leido,
    buscar_mensajes,
    obtener_estadisticas,
    enviar_alerta_actividad,
    obtener_mensajes_actividad,
    obtener_mensajes_proyecto,
    obtener_mensajes_enviados,
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

#Eliminar mensajes
from .views.eliminar_mensajes_views import MensajeViewSet
#Cabiar estado mensajes
from .views.cambiar_estado_view import CambiarEstadoMensajesView



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
    path(r'correos/nuevo-mensaje/', prueba_correo_nuevo_mensaje, name='prueba_correo_nuevo_msg' ),
    ######################### Mensajeria ##########################
    #bandeja
    path(r'mensajes/bandeja/', obtener_bandeja_entrada, name='obtener_bandeja'),
    #Mensajes individuales
    path(r'mensajes/<int:mensaje_id>/', obtener_mensaje, name='obtener_mensaje'),
    path(r'mensajes/enviar/', crear_mensaje_privado, name='enviar_mensaje'),
    path(r'mensajes/<int:mensaje_id>/estado/', actualizar_estado_mensaje, name='actualizar_estado'),
    #Operaciones masivas
    path(r'mensajes/marcar-leidos/', marcar_varios_leido, name='marcar_varios_leido'),
    path(r'marcar-todos-leidos/', marcar_todos_leido, name='marcar_todos_leido'),
    path(r'mensajes/enviados/', obtener_mensajes_enviados, name='obtener_mensajes_enviados'),
    path(r'mensajes/remite-enviar-multiple/', crear_mensaje_multiple, name='enviar_mensaje_multiple'),
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
    #Eliminar mensajes 
    path(r'mensajes/eliminar-multiples/', MensajeViewSet.as_view({'delete': 'eliminar_mensajes'}), name='mensaje-eliminar-multiples'),
    path(r'mensajes/<int:pk>/eliminar/', MensajeViewSet.as_view({'delete': 'eliminar_mensaje'}), name='mensaje-eliminar-individual'),
    #Modificar estados
    path(r'mensajes/cambiar-estado/', CambiarEstadoMensajesView.as_view(), name='mensaje-cambiar-estado'),
] 

urlpatterns += router.urls
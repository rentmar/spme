# spme/spme_planificacion/views/planificacion_proyecto_bulk_historial.vue
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import logging

#Servicios
from ..services.actividad_service import ActividadService

logger = logging.getLogger(__name__)

class ProyectoPlanificacionHistorialView(APIView):
    """
    Endpoint para almacenar la planificacion
    Es extensible, se basa en servicios e implementa transacciones
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user
        data = request.data

        logger.info(f"Planificacion hecho por: {usuario}")

        # === DESESTRUCTURAR PAYLOAD ===
        actividades_actualizar = data.get('actividades_actualizar', [])
        actividades_nuevas = data.get('actividades_nuevas', [])
        tareas_actualizar = data.get('tareas_actualizar', [])
        tareas_nuevas = data.get('tareas_nuevas', [])
        historial_actividades = data.get('historial_actividades', [])
        historial_tareas = data.get('historial_tareas', [])
        estado_anterior = data.get('estado_anterior', {})
        metadatos = data.get('metadatos_seguimiento', {})

        # Extraer metadatos
        proyecto_id = metadatos.get('proyecto_id')
        proyecto_nombre = metadatos.get('proyecto_nombre')
        porque_modificacion = metadatos.get('porque_modificacion')

        
        # === TRANSACCIÓN ===
        try:
            with transaction.atomic():
                # 1. Guardar metadatos de seguimiento
                # 2. Guardar estado anterior (snapshot)
                # 3. Actualizar actividades existentes
                servicio_actividad = ActividadService()
                actualizadas, errores = servicio_actividad.actualizar_actividades(actividades_actualizar)
                # 4. Crear actividades nuevas
                actualizadas = servicio_actividad.actualizar_actividades(actividades_actualizar)
                creadas, mapeo_ids = servicio_actividad.crear_actividades(actividades_nuevas, proyecto_id)
                print(mapeo_ids)
                # 5. Actualizar tareas existentes
                # 6. Crear tareas nuevas
                # 7. Guardar historial de actividades
                # 8. Guardar historial de tareas
                # 9. GUardar la captura del proyecto (estado enterior)
                # 10. Guardar los historiales


                pass

            return Response({
                'msg': 'Planificación guardada correctamente',
                'resumen': {
                    'actividades_actualizadas': len(actividades_actualizar),
                    #'actividades_nuevas': len(actividades_nuevas),
                    #'tareas_actualizar': len(tareas_actualizar),
                    #'tareas_nuevas': len(tareas_nuevas),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error al guardar planificación: {str(e)}")
            return Response({
                'error': 'Error al guardar la planificación',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
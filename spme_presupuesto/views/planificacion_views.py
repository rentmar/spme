from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Servicios
from ..services.planificacion_service import PlanificacionService
from ..services.validacion_service import ValidacionService

#Serializers
from ..serializers.planificacion_serializers import(
    ProyectoPlanificacionSerializer,
    ConsolidadoFuenteSerializer,
    ValidacionActividadSerializer,
    ValidacionProyectoSerializer,
)

#Models
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad

class ProyectoPlanificacionView(APIView):
    """
    Obtiene una vista resumida de la planificacion del proyecto

    Incluye presupuesto global, fuentes, instancias,
    consolidado por fuente y conteo de actividades/tareas.
    """
    #GET
    def get(self, request, proyecto_id):
        try:
            service = PlanificacionService()  
            datos = service.resumen_proyecto(proyecto_id)
            serializer = ProyectoPlanificacionSerializer(datos)
            return Response(serializer.data)        
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

class ActividadesPlanificadasView(APIView):
    """
    Lista las actividades del proyecto con su presupuesto planificado.

    Query params:
        tareas: 'true' para incluir el detalle de tareas (default: false)
    """
    def get(self, request, proyecto_id):
        incluir_tareas = request.query_params.get('tareas', 'false').lower() == 'true'
        try:
            service = PlanificacionService()
            datos = service.actividades_planificadas(proyecto_id, incluir_tareas)
            return Response(datos)
        
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
class TareasPlanificadasView(APIView):
    """
    Obtiene el detalle de tareas planificadas de una actividad.
    
    Incluye la lista de partidas de cada tarea desde presupuestoDesglose.
    """
    def get(self, request, actividad_id):
        try:
            service = PlanificacionService()
            datos = service.tareas_planificadas(actividad_id)
            return Response(datos)
        except Actividad.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
class ConsolidadoFuentesView(APIView):
    """
    Consolida el presupuesto planificado por cada fuente de financiamiento.
    
    Muestra el total planificado por fuente, porcentaje del total,
    y en qué actividades participa cada una.
    """
    def get(self, request, proyecto_id):
        try:
            service = PlanificacionService()
            datos = service.consolidado_por_fuente(proyecto_id)
            serializer = ConsolidadoFuenteSerializer(datos)
            return Response(serializer.data)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        

class ValidarActividadView(APIView):
    """
    Valida que la suma de los montos en procedencia_fondos
    coincida con el presupuesto de la actividad.
    """
    def get(self, request, actividad_id):
        try:
            actividad = Actividad.objects.get(id=actividad_id)
        except Actividad.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        valido, mensaje, suma_fuentes, detalle = (
            ValidacionService.validar_procedencia_fondos_actividad(actividad)
        )

        datos = {
            'valido': valido,
            'actividad_codigo': actividad.codigo or '',
            'presupuesto': actividad.presupuesto or 0,
            'suma_fuentes': suma_fuentes,
            'diferencia': abs(suma_fuentes - float(actividad.presupuesto or 0)),
            'mensaje': mensaje,
            'fuentes_detalle': detalle,
        }

        serializer = ValidacionActividadSerializer(datos)
        
        return Response(serializer.data)
    
class ValidarProyectoView(APIView):
    """
    Valida que el presupuesto global coincida con la suma de actividades.
    El ID del proyecto va en la URL.
    """
    def get(self, request, proyecto_id):
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        valido, mensaje, suma_actividades, detalle = (
            ValidacionService.validar_presupuesto_global(proyecto)
        )

        datos = {
            'valido': valido,
            'proyecto_codigo': proyecto.codigo,
            'presupuesto_proyecto': proyecto.presupuesto or 0,
            'suma_actividades': suma_actividades,
            'diferencia': abs(suma_actividades - float(proyecto.presupuesto or 0)),
            'num_actividades': len(detalle),
            'mensaje': mensaje,
            'actividades_detalle': detalle,
        }

        serializer = ValidacionProyectoSerializer(datos)
        
        return Response(serializer.data)
    
class ValidarTareaView(APIView):
    """
    Valida que la suma de partidas coincida con el presupuesto de la tarea.
    El ID de la tarea va en la URL.
    """
    def get(self, request, tarea_id):
        try:
            tarea = TareaActividad.objects.get(id=tarea_id)
        except TareaActividad.DoesNotExist:
            return Response(
                {'error': 'Tarea no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        valido, mensaje, suma_partidas = ValidacionService.validar_partidas_tarea(tarea)
        return Response({
            'valido': valido,
            'tarea_codigo': tarea.codigo or '',
            'tarea_titulo': tarea.titulo or 'Sin título',
            'presupuesto': tarea.presupuesto or 0,
            'suma_partidas': suma_partidas,
            'diferencia': abs(suma_partidas - float(tarea.presupuesto or 0)),
            'num_partidas': (
                len(tarea.presupuestoDesglose)
                if isinstance(tarea.presupuestoDesglose, list) else 0
            ),
            'mensaje': mensaje,
        })


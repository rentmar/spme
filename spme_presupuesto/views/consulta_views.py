#spme/spme_presupuesto/views/consulta_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from spme_estructuracion_proyecto.models import Proyecto

class EstadoPresupuestoProyectoView(APIView):
    """
    Consulta qué operaciones de presupuesto están habilitadas
    según el estado actual del proyecto. Devuelve las operaciones permitidas
    en el estado actual
    
    Útil para que el frontend habilite/deshabilite botones dinámicamente.
    """
    def get(self, request, proyecto_id):
        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
        except Proyecto.DoesNotExist:
            return Response(
                {'error': 'Proyecto no encontrado.'},
                status=404
            )
        
        #Matriz de permisos por estado
        permisos = {
            'ES': {
                'asociar_fuentes': True,
                'asociar_instancias': True,
                'registrar_presupuesto_proyecto': False,
                'crear_actividades_con_presupuesto': False,
                'desglosar_fuentes_actividad': False,
                'planificar_tareas': False,
                'modificar_libremente': False,
                'requiere_solicitud_modificacion': False,
                'ver_planificacion': False,
                'siguiente_estado': 'Pasar a EP para registrar presupuestos.',
            },
            'EP': {
                'asociar_fuentes': True,
                'asociar_instancias': True,
                'registrar_presupuesto_proyecto': True,
                'crear_actividades_con_presupuesto': True,
                'desglosar_fuentes_actividad': True,
                'planificar_tareas': True,
                'modificar_libremente': True,
                'requiere_solicitud_modificacion': False,
                'ver_planificacion': True,
                'siguiente_estado': 'Pasar a PL para cerrar la planificación.',
            },
            'PL': {
                'asociar_fuentes': True,
                'asociar_instancias': True,
                'registrar_presupuesto_proyecto': False,
                'crear_actividades_con_presupuesto': False,
                'desglosar_fuentes_actividad': False,
                'planificar_tareas': False,
                'modificar_libremente': False,
                'requiere_solicitud_modificacion': True,
                'ver_planificacion': True,
                'siguiente_estado': 'Planificación cerrada. Cambios requieren solicitud formal.',
            },
        }

        estado_info = permisos.get(proyecto.estado, {})
        estado_info.update({
            'proyecto_id': proyecto.id,
            'proyecto_codigo': proyecto.codigo,
            'estado': proyecto.estado,
            'estado_display': proyecto.get_estado_display(),
        })

        return Response(estado_info)


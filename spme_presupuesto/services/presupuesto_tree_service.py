# modules/presupuesto/services/presupuesto_tree_service.py
from typing import Dict, Any, List
from django.db.models import Sum, Count, Q
from spme_repositorio.services.tree import tree_orchestrator
from spme_actividades.models import (Actividad, TareaActividad)
import logging

logger = logging.getLogger(__name__)

class PresupuestoTreeService:
    """
    Servicio para construir la estructura jerárquica del presupuesto.
    """
    
    def __init__(self):
        self.tree_orchestrator = tree_orchestrator
    
    def obtener_estructura_presupuesto(self, proyecto_id: int) -> Dict[str, Any]:
        """
        Obtiene la estructura del proyecto con sus actividades.
        """
        try:
            # 1. Obtener árbol del proyecto
            proyecto_tree = self.tree_orchestrator.build_tree('proyecto', proyecto_id, 'all', 'down')
            proyecto_data = proyecto_tree.to_dict()
            arbol = proyecto_data.get('arbol', {})
            
            # 2. Construir proyecto desde el árbol
            proyecto = self._construir_proyecto(arbol)
            
            # 3. Obtener actividades desde el modelo (más completo)
            actividades = self._obtener_actividades_desde_modelo(proyecto_id)
            
            # 4. Agregar actividades al proyecto
            proyecto['actividades'] = actividades
            
            # 5. Calcular totales
            totales = self._calcular_totales_proyecto(actividades)
            
            return {
                'proyecto': proyecto,
                'totales': totales
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estructura: {str(e)}")
            raise
    
    def _construir_proyecto(self, arbol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye la estructura del proyecto desde el árbol.
        """
        datos = arbol.get('datos', {})
        
        return {
            'id': arbol.get('id'),
            'tipo_nodo': arbol.get('tipo_nodo'),
            'codigo': datos.get('codigo'),
            'titulo': datos.get('titulo'),
            'descripcion': datos.get('descripcion'),
            'fecha_inicio': datos.get('fecha_inicio'),
            'fecha_finalizacion': datos.get('fecha_finalizacion'),
            'presupuesto': datos.get('presupuesto'),
            'estado': datos.get('estado'),
            'propietario': datos.get('propietario'),
            'instancias_gestoras': datos.get('instancias_gestoras', []),
            'procedencia_fondos': datos.get('procedencia_fondos', []),
            'actividades': []
        }
    
    def _obtener_actividades_desde_modelo(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las actividades del proyecto directamente desde el modelo.
        """
        actividades = Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False
        ).select_related(
            'responsable',
            'tipo'
        ).order_by('id')
        
        actividades_list = []
        for actividad in actividades:
            # Obtener tareas de la actividad
            tareas = TareaActividad.objects.filter(
                actividad=actividad
            ).order_by('id')
            
            actividad_data = {
                'id': actividad.id,
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto,
                'descripcion': actividad.descripcion,
                'objetivo': actividad.objetivo_de_actividad,
                'tipo': actividad.tipo.tipo_actividad if actividad.tipo else None,
                'estado': actividad.estado,
                'estado_display': actividad.get_estado_display(),
                'fecha_programada': str(actividad.fecha_programada) if actividad.fecha_programada else None,
                'fecha_inicio': str(actividad.fecha_inicio) if actividad.fecha_inicio else None,
                'fecha_cierre': str(actividad.fecha_cierre) if actividad.fecha_cierre else None,
                'presupuesto': float(actividad.presupuesto) if actividad.presupuesto else 0,
                'presupuesto_global': float(actividad.presupuestoGlobal) if actividad.presupuestoGlobal else 0,
                'total_ejecutado': float(actividad.totalEjecutado) if actividad.totalEjecutado else 0,
                'total_reportado': float(actividad.totalReportado) if actividad.totalReportado else 0,
                'saldo': float(actividad.saldo) if actividad.saldo else 0,
                'grado_ejecucion': actividad.gradoEjecucion,
                'procedencia_fondos': actividad.procedencia_fondos,
                'responsable': {
                    'id': actividad.responsable.id if actividad.responsable else None,
                    'nombre': actividad.responsable.get_full_name() if actividad.responsable else None,
                },
                'total_tareas': tareas.count(),
                'tareas': self._obtener_tareas_actividad(tareas)
            }
            
            actividades_list.append(actividad_data)
        
        return actividades_list
    
    def _obtener_tareas_actividad(self, tareas) -> List[Dict[str, Any]]:
        """
        Obtiene las tareas de una actividad.
        """
        tareas_list = []
        for tarea in tareas:
            tarea_data = {
                'id': tarea.id,
                'codigo': tarea.codigo,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'estado': tarea.estado,
                'estado_display': tarea.get_estado_display(),
                'fecha_ejecucion': str(tarea.fecha_ejecucion) if tarea.fecha_ejecucion else None,
                'fecha_creacion': str(tarea.fecha_creacion) if tarea.fecha_creacion else None,
                'fecha_limite': str(tarea.fecha_limite) if tarea.fecha_limite else None,
                'presupuesto': float(tarea.presupuesto) if tarea.presupuesto else 0,
                'presupuesto_desglose': tarea.presupuestoDesglose,
            }
            tareas_list.append(tarea_data)
        return tareas_list
    
    def _calcular_totales_proyecto(self, actividades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula los totales del proyecto basado en sus actividades.
        """
        totales = {
            'total_actividades': len(actividades),
            'presupuesto_total': sum(a['presupuesto'] for a in actividades),
            'total_ejecutado': sum(a['total_ejecutado'] for a in actividades),
            'total_reportado': sum(a['total_reportado'] for a in actividades),
            'saldo_total': sum(a['saldo'] for a in actividades),
            'total_tareas': sum(a['total_tareas'] for a in actividades),
            'por_estado': {},
            'por_tipo': {}
        }
        
        # Agrupar por estado
        for actividad in actividades:
            estado = actividad['estado_display']
            if estado not in totales['por_estado']:
                totales['por_estado'][estado] = 0
            totales['por_estado'][estado] += 1
        
        # Agrupar por tipo
        for actividad in actividades:
            tipo = actividad['tipo'] or 'No definido'
            if tipo not in totales['por_tipo']:
                totales['por_tipo'][tipo] = 0
            totales['por_tipo'][tipo] += 1
        
        # Porcentaje de ejecución
        if totales['presupuesto_total'] > 0:
            totales['porcentaje_ejecucion'] = round(
                (totales['total_ejecutado'] / totales['presupuesto_total']) * 100, 2
            )
        else:
            totales['porcentaje_ejecucion'] = 0
        
        return totales
# spme_presupuesto/services/arbol_pres_plan_service.py

from ..repositories.arbol_pres_plan_repository import ArbolPresPlanRepository
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad

class ArbolPresPlanService:
    """
    Servicio para construir el árbol de presupuesto planificado.
    Responsabilidad: Lógica de negocio y construcción de nodos recursivos.
    Niveles: 0=Proyecto, 1=Actividad, 2=Tarea
    """
    
    def __init__(self):
        self.repository = ArbolPresPlanRepository()
    
    def construir_arbol(self, proyecto_id):
        """
        Construye el árbol presupuestario completo.
        
        Args:
            proyecto_id (int): ID del proyecto
            
        Returns:
            dict or None: Árbol presupuestario o None si el proyecto no existe
        """
        try:
            proyecto = self.repository.obtener_proyecto(proyecto_id)
            return self._nodo_proyecto(proyecto)
        except Proyecto.DoesNotExist:
            return None
    
    # ═══════════════════════════════════════════════════════
    # NODO PROYECTO (Nivel 0)
    # ═══════════════════════════════════════════════════════
    
    def _nodo_proyecto(self, proyecto):
        """
        Construye el nodo raíz del árbol: Proyecto.
        Incluye todas las actividades, tareas y resúmenes.
        """
        presupuesto = float(proyecto.presupuesto or 0)
        actividades = proyecto.actividad_proyecto.filter(estaInactiva=False)
        
        # Separar actividades válidas (no CRD)
        validas = [a for a in actividades if a.estado != 'CRD']
        
        # Cálculos del resumen
        total_planificado = sum(float(a.presupuesto or 0) for a in validas)
        saldo = presupuesto - total_planificado
        
        # Sumar por financiador
        financiadores_resumen = self._sumar_por_financiador(validas)
        
        # Actividades sin desglose
        sin_desglose = [
            {
                'id': a.id,
                'codigo': a.codigo,
                'nombre': a.nombreCorto,
                'presupuesto': float(a.presupuesto or 0),
            }
            for a in validas
            if not a.procedencia_fondos or len(a.procedencia_fondos) == 0
        ]
        
        return {
            'tipo_nodo': 'proyecto',
            'id': proyecto.id,
            'nivel': 0,
            'datos': {
                # Información básica
                'codigo': proyecto.codigo,
                'titulo': proyecto.titulo,
                'descripcion': proyecto.descripcion or '',
                
                # Fechas
                'fecha_inicio': str(proyecto.fecha_inicio) if proyecto.fecha_inicio else '',
                'fecha_finalizacion': str(proyecto.fecha_finalizacion) if proyecto.fecha_finalizacion else '',
                
                # Presupuesto
                'presupuesto': presupuesto,
                'presupuesto_planificado': total_planificado,
                'saldo': saldo,
                
                # Estado
                'estado': proyecto.get_estado_display() if proyecto.estado else '',
                'estado_codigo': proyecto.estado or '',
                
                # Relaciones
                'pei': str(proyecto.pei) if proyecto.pei else '',
                'programa': str(proyecto.programa) if proyecto.programa else '',
                'propietario': proyecto.propietario.get_full_name() if proyecto.propietario else '',
                
                # Listas
                'instancias_gestoras': self._formatear_instancias(proyecto),
                'procedencia_fondos': self._formatear_fondos(proyecto),
                
                # Flags
                'esta_habilitado': proyecto.esta_habilitado,
            },
            'actividades': [
                # Cada actividad individual con sus tareas
                *[self._nodo_actividad(a) for a in actividades],
                # Resumen general de actividades
                {
                    'tipo_nodo': 'resumen_actividades',
                    'id': None,
                    'nivel': 1,
                    'datos': {
                        'total_actividades': actividades.count(),
                        'actividades_validas': len(validas),
                        'actividades_excluidas': actividades.count() - len(validas),
                        'presupuesto_planificado': total_planificado,
                        'saldo': saldo,
                        'porcentaje': self._porcentaje(total_planificado, presupuesto),
                        'excedido': saldo < 0,
                        'financiadores': financiadores_resumen,
                        'actividades_sin_desglose': sin_desglose,
                    },
                    'metadata': {}
                },
            ],
            'metadata': {
                'presupuesto_total': presupuesto,
                'total_planificado': total_planificado,
                'saldo': saldo,
                'porcentaje': self._porcentaje(total_planificado, presupuesto),
                'estado_proyecto': proyecto.get_estado_display() if proyecto.estado else '',
                'nodo_inicio': f'proyecto:{proyecto.id}',
                'nivel_actual': 0,
                'total_actividades': actividades.count(),
                'actividades_validas': len(validas),
            }
        }
    
    # ═══════════════════════════════════════════════════════
    # NODO ACTIVIDAD (Nivel 1)
    # ═══════════════════════════════════════════════════════
    
    def _nodo_actividad(self, actividad):
        """
        Construye el nodo de una actividad individual.
        Incluye datos generales, presupuesto, desglose, tareas y resumen.
        """
        presupuesto = float(actividad.presupuesto or 0)
        desglose = actividad.procedencia_fondos or []
        valida = actividad.estado != 'CRD'
        tareas = actividad.tareas.all()
        
        # Cálculos de tareas
        total_tareas = sum(float(t.presupuesto or 0) for t in tareas)
        saldo_tareas = presupuesto - total_tareas
        
        return {
            'tipo_nodo': 'actividad',
            'id': actividad.id,
            'nivel': 1,
            'datos': {
                # Información de la actividad
                'codigo': actividad.codigo,
                'nombre': actividad.nombreCorto,
                'descripcion': actividad.descripcion or '',
                'estado': actividad.estado,
                'estado_display': dict(Actividad.ESTADOS_ACTIVIDAD).get(actividad.estado, actividad.estado),
                'fecha_inicio': str(actividad.fecha_inicio) if actividad.fecha_inicio else '',
                'fecha_cierre': str(actividad.fecha_cierre) if actividad.fecha_cierre else '',
                'responsable': actividad.responsable.get_full_name() if actividad.responsable else '',
                'tipo_actividad': str(actividad.tipo) if actividad.tipo else '',
                
                # Presupuesto
                'presupuesto': presupuesto,
                'presupuesto_global': float(actividad.presupuestoGlobal or 0),
                'valida': valida,
                'tiene_desglose': len(desglose) > 0,
                
                # Tareas
                'total_tareas': tareas.count(),
                'presupuesto_total_tareas': total_tareas,
                'saldo_tareas': saldo_tareas,
                'porcentaje_tareas': self._porcentaje(total_tareas, presupuesto),
                'excedido_tareas': total_tareas > presupuesto,
            },
            'presupuesto': {
                'total': presupuesto,
                'procedencia_fondos': self._formatear_desglose(desglose),
            },
            'tareas': [
                # Cada tarea individual
                *[self._nodo_tarea(t) for t in tareas],
                # Resumen de tareas
                {
                    'tipo_nodo': 'resumen_tareas',
                    'id': None,
                    'nivel': 2,
                    'datos': {
                        'total_tareas': tareas.count(),
                        'presupuesto_total_tareas': total_tareas,
                        'saldo': saldo_tareas,
                        'porcentaje': self._porcentaje(total_tareas, presupuesto),
                        'excedido': total_tareas > presupuesto,
                    },
                    'metadata': {}
                },
            ],
            'resumen': {
                'presupuesto': presupuesto,
                'procedencia_fondos': self._sumar_desglose(desglose),
                'total_tareas': total_tareas,
                'saldo_tareas': saldo_tareas,
            },
            'metadata': {
                'es_valida': valida,
                'tiene_desglose': len(desglose) > 0,
                'total_tareas': tareas.count(),
            }
        }
    
    # ═══════════════════════════════════════════════════════
    # NODO TAREA (Nivel 2)
    # ═══════════════════════════════════════════════════════
    
    def _nodo_tarea(self, tarea):
        """
        Construye el nodo de una tarea individual.
        Incluye datos generales, presupuesto y desglose.
        """
        presupuesto = float(tarea.presupuesto or 0)
        desglose = tarea.presupuestoDesglose or []
        tiene_desglose = len(desglose) > 0
        
        return {
            'tipo_nodo': 'tarea',
            'id': tarea.id,
            'nivel': 2,
            'datos': {
                # Información de la tarea
                'codigo': tarea.codigo,
                'titulo': tarea.titulo or 'Sin título',
                'descripcion': tarea.descripcion or '',
                'estado': tarea.estado,
                'estado_display': dict(TareaActividad.ESTADOS_TAREA).get(tarea.estado, tarea.estado),
                'fecha_creacion': str(tarea.fecha_creacion) if tarea.fecha_creacion else '',
                'fecha_limite': str(tarea.fecha_limite) if tarea.fecha_limite else '',
                'fecha_ejecucion': str(tarea.fecha_ejecucion) if tarea.fecha_ejecucion else '',
                
                # Presupuesto
                'presupuesto': presupuesto,
                'tiene_desglose': tiene_desglose,
            },
            'presupuesto': {
                'total': presupuesto,
                'desglose': self._formatear_desglose_tarea(desglose),
            },
            'resumen': {
                'presupuesto': presupuesto,
                'desglose_total': self._sumar_desglose_tarea(desglose),
            },
            'metadata': {
                'tiene_desglose': tiene_desglose,
            }
        }
    
    # ═══════════════════════════════════════════════════════
    # FORMATEADORES Y CÁLCULOS
    # ═══════════════════════════════════════════════════════
    
    def _porcentaje(self, parcial, total):
        """Calcula el porcentaje con 1 decimal"""
        return round((parcial / total * 100), 1) if total > 0 else 0
    
    def _formatear_instancias(self, proyecto):
        """Formatea las instancias gestoras del proyecto"""
        return [
            {
                'codigo': ig.codigo,
                'instancia': ig.instancia,
                'clasificador': ig.clasificador or '',
            }
            for ig in proyecto.instancia_gestora.all()
        ]
    
    def _formatear_fondos(self, proyecto):
        """Formatea la procedencia de fondos del proyecto (incluye id)"""
        return [
            {
                'id': pf.id,
                'sigla': pf.sigla,
                'financiera': pf.financiera,
            }
            for pf in proyecto.procedencia_fondos.all()
        ]
    
    def _formatear_desglose(self, desglose):
        """Formatea el desglose de una actividad"""
        return [
            {
                'id': d.get('id'),
                'nombre': d.get('nombre', d.get('financiera', '')),
                'monto': float(d.get('monto', 0)),
                'es_existente': d.get('esExistente', False),
                'manual': d.get('manual', False),
            }
            for d in desglose
        ]
    
    def _formatear_desglose_tarea(self, desglose):
        """Formatea el desglose de una tarea"""
        return [
            {
                'partida': d.get('partida', ''),
                'descripcion': d.get('descripcion', ''),
                'monto': float(d.get('monto', 0)),
            }
            for d in desglose
        ]
    
    def _sumar_desglose(self, desglose):
        """Suma los montos de un desglose de actividad"""
        return sum(float(d.get('monto', 0)) for d in desglose)
    
    def _sumar_desglose_tarea(self, desglose):
        """Suma los montos del desglose de una tarea"""
        return sum(float(d.get('monto', 0)) for d in desglose)
    
    def _sumar_por_financiador(self, actividades):
        """
        Suma los montos por financiador de todas las actividades válidas.
        
        Reglas:
        - Existentes (es_existente=True): se agrupan por id
        - Manuales (es_existente=False): cada uno es único, se agregan individualmente
        """
        resumen = {}
        for a in actividades:
            for d in (a.procedencia_fondos or []):
                id_fin = d.get('id')
                nombre = d.get('nombre', d.get('financiera', ''))
                monto = float(d.get('monto', 0))
                es_existente = d.get('esExistente', False)
                
                if es_existente and id_fin:
                    if id_fin not in resumen:
                        resumen[id_fin] = {
                            'id': id_fin,
                            'nombre': nombre,
                            'monto': 0,
                            'es_existente': True,
                        }
                    resumen[id_fin]['monto'] += monto
                else:
                    clave = f'manual_{id_fin}'
                    resumen[clave] = {
                        'id': id_fin,
                        'nombre': nombre,
                        'monto': monto,
                        'es_existente': False,
                    }
        
        return list(resumen.values())
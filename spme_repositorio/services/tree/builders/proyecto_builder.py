#Constructor del nodo Proyecto
from typing import Optional, List
from ..base import BaseNodeBuilder
from ..dto import TreeNode
from ..enums import NodeType
from spme_estructuracion_proyecto.models import (
    Proyecto, 
    ObjetivoGeneralProyecto,
)


class ProyectoBuilder(BaseNodeBuilder):
    """Builder para nodos de tipo Proyecto"""
    
    def get_node_type(self) -> str:
        return NodeType.PROYECTO
    
    def get_ids_by_parent(self, parent_id, parent_type: str) -> List:
        """
        No aplica: Proyecto es raíz, no tiene padre directo en esta estructura.
        Retorna vacío.
        """
        return []
    
    def get_parent_id(self, child_id, parent_type: str) -> Optional[int]:
        """
        No aplica: Proyecto es raíz.
        """
        return None
    
    def build(self, node_id, nivel=0, es_nodo_objetivo=False, depth_remaining=None, build_context=None) -> TreeNode:
        try:
            proyecto = Proyecto.objects.select_related(
                'pei', 'programa', 'propietario'
            ).prefetch_related(
                'instancia_gestora',
                'procedencia_fondos'
            ).get(id=node_id, esta_habilitado=True)
            
            datos = self._extract_data(proyecto)
            
            return self._create_node(
                tipo_nodo=NodeType.PROYECTO.value,
                node_id=proyecto.id,
                nivel=nivel,
                datos=datos,
                es_nodo_objetivo=es_nodo_objetivo
            )
            
        except Proyecto.DoesNotExist:
            raise ValueError(f"Proyecto con ID {node_id} no encontrado o no está habilitado")
    
    def _extract_data(self, proyecto: Proyecto) -> dict:
        return {
            'codigo': proyecto.codigo,
            'titulo': proyecto.titulo,
            'descripcion': proyecto.descripcion or '',
            'fecha_inicio': proyecto.fecha_inicio.isoformat() if proyecto.fecha_inicio else None,
            'fecha_finalizacion': proyecto.fecha_finalizacion.isoformat() if proyecto.fecha_finalizacion else None,
            'presupuesto': str(proyecto.presupuesto) if proyecto.presupuesto else '0.00',
            'estado': proyecto.get_estado_display(),
            'pei': proyecto.pei.titulo if proyecto.pei else None,
            'programa': proyecto.programa.nombre if proyecto.programa else None,
            'propietario': proyecto.propietario.get_full_name() if proyecto.propietario else None,
            'instancias_gestoras': [
                ig.instancia for ig in proyecto.instancia_gestora.all()
            ],
            'procedencia_fondos': [
                {
                    'sigla': pf.sigla,
                    'financiera': pf.financiera
                } for pf in proyecto.procedencia_fondos.all()
            ],
            'tiene_objetivo_general': hasattr(proyecto, 'objetivo_general') and proyecto.objetivo_general is not None
        }
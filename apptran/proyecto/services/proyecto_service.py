# spme/apptran/proyecto/services/proyecto_service.py
from ..repositories.proyecto_repository import ProyectoRepository
from ..serializers.proyecto_serializers import (
    ProyectoConActividadesSerializer,
    ActividadConTareasSerializer
)
from rest_framework.exceptions import NotFound
#importacion del servicio para el calculo de los press ejecutados
from spme_presupuesto.services.presupuesto_tree.calculos_presupuestos_ejecutados import (
    obtener_totales_actividad,
    obtener_totales_tarea,
)

import logging

#Agregar el logger
logger = logging.getLogger(__name__)

class ProyectoService:
    """
    Servicio para la lógica de negocio relacionada con Proyectos
    """
    
    def __init__(self):
        self.proyecto_repository = ProyectoRepository()
    
    def obtener_estructura_proyecto(self, proyecto_id):
        """
        Obtiene la estructura jerárquica completa:
        Proyecto → Actividades → Tareas
        
        Args:
            proyecto_id (int): ID del proyecto
            
        Returns:
            dict: Diccionario con la estructura completa y metadatos
            
        Raises:
            NotFound: Si el proyecto no existe o no está habilitado
        """
        # Verificar que el proyecto existe
        proyecto = self.proyecto_repository.get_proyecto_por_id(proyecto_id)
        
        if not proyecto:
            raise NotFound(
                detail=f"Proyecto con ID {proyecto_id} no encontrado o no está habilitado"
            )
        
        # Obtener proyecto con toda su estructura
        proyecto_completo = self.proyecto_repository.get_proyecto_con_estructura_completa(
            proyecto_id
        )
        
        if not proyecto_completo:
            raise NotFound(
                detail="Error al obtener la estructura del proyecto"
            )
        
        # Serializar los datos
        serializer = ProyectoConActividadesSerializer(proyecto_completo)
        data = serializer.data

        #Agregar los datos presupuestarios
        data = self._enriquecer_con_presupuestos(data)
        
        # Calcular total de actividades activas
        total_actividades = proyecto.actividad_proyecto.filter(
            estaInactiva=False
        ).count()
        
        return {
            'success': True,
            'data': data,
            'metadata': {
                'proyecto_id': proyecto.id,
                'codigo_proyecto': proyecto.codigo,
                'total_actividades': total_actividades,
                'estado_proyecto': proyecto.estado
            }
        }


    def obtener_actividades_inactivas(self, proyecto_id):
        """
        Obtiene solo las actividades INACTIVAS de un proyecto con sus tareas
        
        Args:
            proyecto_id (int): ID del proyecto
            
        Returns:
            dict: Diccionario con las actividades inactivas y metadatos
            
        Raises:
            NotFound: Si el proyecto no existe
        """
        # Verificar que el proyecto existe
        proyecto = self.proyecto_repository.get_proyecto_por_id(proyecto_id)
        
        if not proyecto:
            raise NotFound(
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )
        
        # Obtener solo las actividades inactivas
        actividades_inactivas = proyecto.actividad_proyecto.filter(
            estaInactiva=True
        ).prefetch_related('tareas').order_by('fecha_programada', 'codigo')
        
        # Serializar
        serializer = ActividadConTareasSerializer(actividades_inactivas, many=True)
        
        # Obtener totales para metadata
        total_actividades = proyecto.actividad_proyecto.count()
        total_activas = proyecto.actividad_proyecto.filter(estaInactiva=False).count()
        total_inactivas = actividades_inactivas.count()
        
        return {
            'success': True,
            'data': {
                'proyecto_id': proyecto.id,
                'proyecto_codigo': proyecto.codigo,
                'proyecto_titulo': proyecto.titulo,
                'actividades_inactivas': serializer.data
            },
            'metadata': {
                'total_actividades': total_actividades,
                'actividades_activas': total_activas,
                'actividades_inactivas': total_inactivas
            }
        }
    
    def obtener_actividades_del_proyecto(self, proyecto_id):
        """
        Obtiene solo las actividades de un proyecto con sus tareas
        VERSIÓN CORREGIDA - Usa el mismo approach que obtener_estructura_proyecto
        
        Args:
            proyecto_id (int): ID del proyecto
            
        Returns:
            dict: Diccionario con las actividades y metadatos
            
        Raises:
            NotFound: Si el proyecto no existe
        """
        # Verificar que el proyecto existe (igual que en el método que funciona)
        proyecto = self.proyecto_repository.get_proyecto_por_id(proyecto_id)
        
        if not proyecto:
            raise NotFound(
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )
        
        # USAR EL MISMO ENFOQUE QUE FUNCIONA EN obtener_estructura_proyecto
        # En lugar de usar get_actividades_con_tareas, usar el related_name del proyecto
        actividades = proyecto.actividad_proyecto.filter(
            estaInactiva=False
        ).prefetch_related('tareas').order_by('id')
        actividades = sorted(actividades, key=lambda a: a.id)
        # actividades = proyecto.actividad_proyecto.filter(
        #     estaInactiva=False
        # ).prefetch_related('tareas').order_by('fecha_programada', 'codigo')
        
        # Serializar
        serializer = ActividadConTareasSerializer(actividades, many=True)
        
        return {
            'success': True,
            'data': {
                'proyecto_id': proyecto.id,
                'proyecto_codigo': proyecto.codigo,
                'proyecto_titulo': proyecto.titulo,
                'actividades': serializer.data
            },
            'total_actividades': actividades.count()
        }

    def _enriquecer_con_presupuestos(self, data):
        """
        Agrega información de total reportado a cada actividad y tarea
        """
        try:
            if isinstance(data, dict) and 'actividades' in data:
                data['actividades'] = [
                    self._enriquecer_actividad(actividad) 
                    for actividad in data['actividades']
                ]
            return data
        except Exception as e:
            logger.error(f"Error al enriquecer con presupuestos: {str(e)}")
            return data

    def _enriquecer_actividad(self, actividad):
        """
        Enriquece una actividad individual con el total reportado
        """
        if not isinstance(actividad, dict):
            return actividad
        
        actividad_id = actividad.get('id')
        
        if actividad_id:
            try:
                totales = obtener_totales_actividad(actividad_id)
                actividad['totalReportado'] = float(totales.get('presupuesto_ejecutado', 0))
                logger.info(f"Actividad {actividad_id}: totalReportado={totales.get('presupuesto_ejecutado', 0)}")
            except Exception as e:
                logger.warning(f"No se pudieron obtener totales para actividad {actividad_id}: {str(e)}")
                if 'totalReportado' not in actividad:
                    actividad['totalReportado'] = 0.0
        
        tareas = actividad.get('tareas', [])
        if tareas:
            actividad['tareas'] = [
                self._enriquecer_tarea(tarea) 
                for tarea in tareas
            ]
        
        return actividad

    def _enriquecer_actividad(self, actividad):
        """
        Enriquece una actividad individual con el total reportado
        """
        if not isinstance(actividad, dict):
            return actividad
        
        actividad_id = actividad.get('id')
        
        if actividad_id:
            try:
                totales = obtener_totales_actividad(actividad_id)
                actividad['totalReportado'] = float(totales.get('presupuesto_ejecutado', 0))
                logger.info(f"Actividad {actividad_id}: totalReportado={totales.get('presupuesto_ejecutado', 0)}")
            except Exception as e:
                logger.warning(f"No se pudieron obtener totales para actividad {actividad_id}: {str(e)}")
                if 'totalReportado' not in actividad:
                    actividad['totalReportado'] = 0.0
        
        tareas = actividad.get('tareas', [])
        if tareas:
            actividad['tareas'] = [
                self._enriquecer_tarea(tarea) 
                for tarea in tareas
            ]
        
        return actividad
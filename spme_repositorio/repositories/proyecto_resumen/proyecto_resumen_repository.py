# spme/spme_repositorio/repositories/proyecto_resumen/proyecto_resumen_repository.py
from typing import List, Dict, Any
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count, Prefetch
from django.core.cache import cache

from spme_estructuracion_proyecto.models import (
    Proyecto,
    ObjetivoGeneralProyecto,
    ObjetivoEspecificoProyecto,
    IndicadorObjetivoGeneral,
    ResultadoOG,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    ResultadoOE,
    IndicadorResultadoObjEspecifico,
)
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso,
    SolicitudViaje,
    SolicitudPagoDirecto,
    RendicionCuentas,
    InformeActividadPrincipal,
    InformeTareaPrincipal,
)
from spme_repositorio.models import Adjunto, ReferenciaExterna
import logging

logger = logging.getLogger(__name__)

class ProyectoResumenRepository:
    """Repositorio optimizado para consultas de resumen."""
    
    # Cache para ContentTypes (evita queries repetidas)
    _content_type_cache: Dict[str, int] = {}
    
    def get_proyectos_habilitados(self):
        """Retorna proyectos habilitados con prefetch optimizado."""
        return Proyecto.objects.filter(
            esta_habilitado=True
        ).prefetch_related(
            'instancia_gestora'
        ).only(
            'id', 'titulo', 'codigo', 'descripcion', 
            'estado', 'fecha_creacion', 'propietario_id'
        )
    
    def get_all_content_types(self, modelos: List[type]) -> Dict[str, int]:
        """
        Obtiene todos los ContentTypes en una sola query.
        Retorna diccionario {modelo.__name__: content_type_id}
        """
        if self._content_type_cache:
            return self._content_type_cache
            
        from django.contrib.contenttypes.models import ContentType
        
        model_names = [m.__name__.lower() for m in modelos]
        
        content_types = ContentType.objects.filter(
            model__in=model_names
        ).values('model', 'id')
        
        self._content_type_cache = {
            ct['model']: ct['id'] 
            for ct in content_types
        }
        
        return self._content_type_cache
    
    def get_all_adjuntos_por_proyecto(self, proyecto_id: int) -> Dict[str, List]:
        """
        Obtiene TODOS los adjuntos del proyecto en una sola query.
        Retorna diccionario agrupado por content_type y object_id.
        """
        from spme_repositorio.models import Adjunto
        
        adjuntos = Adjunto.objects.filter(
            object_id__in=self._get_all_object_ids(proyecto_id)
        ).select_related('archivo')
        
        # Agrupar por (content_type_id, object_id)
        adjuntos_agrupados = {}
        for adj in adjuntos:
            key = f"{adj.content_type_id}:{adj.object_id}"
            if key not in adjuntos_agrupados:
                adjuntos_agrupados[key] = []
            adjuntos_agrupados[key].append(adj)
        
        return adjuntos_agrupados
    
    def get_all_referencias_por_proyecto(self, proyecto_id: int) -> Dict[str, int]:
        """
        Obtiene TODAS las referencias del proyecto en una sola query.
        Retorna diccionario con conteos.
        """
        from spme_repositorio.models import ReferenciaExterna
        
        referencias = ReferenciaExterna.objects.filter(
            object_id__in=self._get_all_object_ids(proyecto_id)
        ).values('content_type_id', 'object_id').annotate(
            total=Count('id')
        )
        
        referencias_agrupadas = {}
        for ref in referencias:
            key = f"{ref['content_type_id']}:{ref['object_id']}"
            referencias_agrupadas[key] = ref['total']
        
        return referencias_agrupadas
    
    def _get_all_object_ids(self, proyecto_id: int) -> List[int]:
        """
        Obtiene TODOS los IDs de todos los objetos relacionados al proyecto.
        Esta es la clave para hacer queries masivas.
        """
        ids = [proyecto_id]
        
        # Objetivos generales
        og_ids = list(ObjetivoGeneralProyecto.objects.filter(
            proyecto_id=proyecto_id
        ).values_list('id', flat=True))
        ids.extend(og_ids)
        
        if not og_ids:
            return ids
        
        # Indicadores OG
        ids.extend(IndicadorObjetivoGeneral.objects.filter(
            objetivo_general_id__in=og_ids
        ).values_list('id', flat=True))
        
        # Resultados OG
        rog_ids = list(ResultadoOG.objects.filter(
            objetivo_general_id__in=og_ids
        ).values_list('id', flat=True))
        ids.extend(rog_ids)
        
        # Indicadores ROG
        if rog_ids:
            ids.extend(IndicadorResultadoObjGral.objects.filter(
                resultado_og_id__in=rog_ids
            ).values_list('id', flat=True))
        
        # Objetivos específicos
        oe_ids = list(ObjetivoEspecificoProyecto.objects.filter(
            objetivo_general_id__in=og_ids
        ).values_list('id', flat=True))
        ids.extend(oe_ids)
        
        if oe_ids:
            # Indicadores OE
            ids.extend(IndicadorObjetivoEspecifico.objects.filter(
                objetivo_especifico_id__in=oe_ids
            ).values_list('id', flat=True))
            
            # Resultados OE
            roe_ids = list(ResultadoOE.objects.filter(
                objetivo_especifico_id__in=oe_ids
            ).values_list('id', flat=True))
            ids.extend(roe_ids)
            
            # Indicadores ROE
            if roe_ids:
                ids.extend(IndicadorResultadoObjEspecifico.objects.filter(
                    resultado_obj_especifico_id__in=roe_ids
                ).values_list('id', flat=True))
        
        # Actividades
        act_ids = list(Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False,
        ).values_list('id', flat=True))
        ids.extend(act_ids)
        
        if act_ids:
            # Tareas
            tarea_ids = list(TareaActividad.objects.filter(
                actividad_id__in=act_ids
            ).values_list('id', flat=True))
            ids.extend(tarea_ids)
            
            # Solicitudes y rendiciones
            solicitudes_ids = list(SolicitudFondos.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            ids.extend(solicitudes_ids)
            
            solicitudes_ids = list(SolicitudReembolso.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            ids.extend(solicitudes_ids)
            
            solicitudes_ids = list(SolicitudViaje.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            ids.extend(solicitudes_ids)
            
            solicitudes_ids = list(SolicitudPagoDirecto.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            ids.extend(solicitudes_ids)
            
            rendiciones_ids = list(RendicionCuentas.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            ids.extend(rendiciones_ids)
            
            # Informes
            ids.extend(InformeActividadPrincipal.objects.filter(
                actividad_id__in=act_ids
            ).values_list('id', flat=True))
            
            if tarea_ids:
                ids.extend(InformeTareaPrincipal.objects.filter(
                    tarea_id__in=tarea_ids
                ).values_list('id', flat=True))
        
        return list(set(ids))  # Eliminar duplicados
# spme/spme_repositorio/services/proyecto_resumen/proyecto_resumen_service.py
from typing import Dict, Any, List, Set
from django.core.cache import cache
from django.db.models import Count, Q

import logging

from spme_repositorio.repositories.proyecto_resumen.proyecto_resumen_repository import (
    ProyectoResumenRepository,
)

from spme_estructuracion_proyecto.models import (
    Proyecto,
    ObjetivoGeneralProyecto,
    IndicadorObjetivoGeneral,
    ResultadoOG,
    IndicadorResultadoObjGral,
    ObjetivoEspecificoProyecto,
    IndicadorObjetivoEspecifico,
    ResultadoOE,
    IndicadorResultadoObjEspecifico,
)
from spme_actividades.models import(
    Actividad,
    TareaActividad,
)

from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudReembolso,
    RendicionCuentas,
    InformeActividadPrincipal,
    InformeTareaPrincipal,
)

from spme_repositorio.models import (
    Adjunto,
    ReferenciaExterna,
)

logger = logging.getLogger(__name__)


class ProyectoResumenService:
    """Servicio optimizado sin caché."""
    
    TIPO_MAPEO = {
        'DOCUMENTO': 'documentos',
        'IMAGEN': 'imagenes',
        'VIDEO': 'videos',
        'AUDIO': 'audios',
        'OTRO': 'otros',
    }
    
    def __init__(self):
        self._repo = ProyectoResumenRepository()
    
    def generar_resumen_completo(self) -> list:
        """
        Genera resumen optimizado.
        Antes: ~500 queries para 10 proyectos
        Ahora: ~10 queries en total
        """
        proyectos = self._repo.get_proyectos_habilitados()
        
        if not proyectos:
            return []
        
        # 1. Obtener TODOS los IDs de objetos relacionados (1 query por modelo)
        all_object_ids = self._get_all_object_ids(proyectos)
        
        # 2. Obtener TODOS los adjuntos en UNA query
        adjuntos_data = self._get_all_adjuntos_data(all_object_ids)
        
        # 3. Obtener TODAS las referencias en UNA query
        referencias_data = self._get_all_referencias_data(all_object_ids)
        
        # 4. Obtener ContentTypes en UNA query
        content_types = self._get_content_types()
        
        # 5. Generar resumen para cada proyecto usando datos precargados
        resultado = []
        for proyecto in proyectos:
            resumen = self._generar_resumen_proyecto(
                proyecto,
                content_types,
                adjuntos_data,
                referencias_data
            )
            resultado.append(resumen)
        
        return resultado
    
    def _get_all_object_ids(self, proyectos) -> Set[int]:
        """
        Obtiene TODOS los IDs de objetos relacionados en queries masivas.
        """
        proyecto_ids = [p.id for p in proyectos]
        all_ids = set(proyecto_ids)
        
        # 1 query por modelo, no por instancia
        og_ids = set(ObjetivoGeneralProyecto.objects.filter(
            proyecto_id__in=proyecto_ids
        ).values_list('id', flat=True))
        all_ids.update(og_ids)
        
        if og_ids:
            # Indicadores OG
            all_ids.update(IndicadorObjetivoGeneral.objects.filter(
                objetivo_general_id__in=og_ids
            ).values_list('id', flat=True))
            
            # Resultados OG
            rog_ids = set(ResultadoOG.objects.filter(
                objetivo_general_id__in=og_ids
            ).values_list('id', flat=True))
            all_ids.update(rog_ids)
            
            if rog_ids:
                all_ids.update(IndicadorResultadoObjGral.objects.filter(
                    resultado_og_id__in=rog_ids
                ).values_list('id', flat=True))
            
            # Objetivos específicos
            oe_ids = set(ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general_id__in=og_ids
            ).values_list('id', flat=True))
            all_ids.update(oe_ids)
            
            if oe_ids:
                all_ids.update(IndicadorObjetivoEspecifico.objects.filter(
                    objetivo_especifico_id__in=oe_ids
                ).values_list('id', flat=True))
                
                roe_ids = set(ResultadoOE.objects.filter(
                    objetivo_especifico_id__in=oe_ids
                ).values_list('id', flat=True))
                all_ids.update(roe_ids)
                
                if roe_ids:
                    all_ids.update(IndicadorResultadoObjEspecifico.objects.filter(
                        resultado_obj_especifico_id__in=roe_ids
                    ).values_list('id', flat=True))
        
        # Actividades
        act_ids = set(Actividad.objects.filter(
            proyecto_id__in=proyecto_ids,
            estaInactiva=False,
        ).values_list('id', flat=True))
        all_ids.update(act_ids)
        
        if act_ids:
            # Tareas
            tarea_ids = set(TareaActividad.objects.filter(
                actividad_id__in=act_ids
            ).values_list('id', flat=True))
            all_ids.update(tarea_ids)
            
            # Solicitudes (4 modelos)
            for modelo in [SolicitudFondos, SolicitudReembolso, 
                          SolicitudViaje, SolicitudPagoDirecto]:
                all_ids.update(modelo.objects.filter(
                    Q(actividad_id__in=act_ids) | 
                    Q(tarea_id__in=tarea_ids)
                ).values_list('id', flat=True))
            
            # Rendiciones
            all_ids.update(RendicionCuentas.objects.filter(
                Q(actividad_id__in=act_ids) | 
                Q(tarea_id__in=tarea_ids)
            ).values_list('id', flat=True))
            
            # Informes
            all_ids.update(InformeActividadPrincipal.objects.filter(
                actividad_id__in=act_ids
            ).values_list('id', flat=True))
            
            if tarea_ids:
                all_ids.update(InformeTareaPrincipal.objects.filter(
                    tarea_id__in=tarea_ids
                ).values_list('id', flat=True))
        
        return all_ids
    
    def _get_all_adjuntos_data(self, all_object_ids: Set[int]) -> Dict[str, List[str]]:
        """
        Obtiene TODOS los adjuntos en UNA SOLA query.
        Retorna: {(content_type_id, object_id): [tipo_archivo1, tipo_archivo2, ...]}
        """
        adjuntos = Adjunto.objects.filter(
            object_id__in=all_object_ids
        ).select_related('archivo').values(
            'content_type_id', 
            'object_id', 
            'archivo__tipo_archivo'
        )
        
        adjuntos_agrupados = {}
        for adj in adjuntos:
            key = f"{adj['content_type_id']}:{adj['object_id']}"
            if key not in adjuntos_agrupados:
                adjuntos_agrupados[key] = []
            
            tipo = adj['archivo__tipo_archivo'] or 'OTRO'
            adjuntos_agrupados[key].append(tipo)
        
        return adjuntos_agrupados
    
    def _get_all_referencias_data(self, all_object_ids: Set[int]) -> Dict[str, int]:
        """
        Obtiene TODAS las referencias en UNA SOLA query.
        Retorna: {(content_type_id, object_id): total_referencias}
        """
        referencias = ReferenciaExterna.objects.filter(
            object_id__in=all_object_ids
        ).values('content_type_id', 'object_id').annotate(
            total=Count('id')
        )
        
        referencias_agrupadas = {}
        for ref in referencias:
            key = f"{ref['content_type_id']}:{ref['object_id']}"
            referencias_agrupadas[key] = ref['total']
        
        return referencias_agrupadas
    
    def _get_content_types(self) -> Dict[str, int]:
        """
        Obtiene todos los ContentTypes necesarios en UNA query.
        Retorna: {modelo_name: content_type_id}
        """
        from django.contrib.contenttypes.models import ContentType
        
        modelos_necesarios = [
            'proyecto',
            'objetivogeneralproyecto',
            'objetivoespecificoproyecto',
            'indicadorobjetivogeneral',
            'resultadoog',
            'indicadorresultadoobjgral',
            'indicadorobjetivoespecifico',
            'resultadooe',
            'indicadorresultadoobjespecifico',
            'actividad',
            'tareaactividad',
            'solicitudfondos',
            'solicitudreembolso',
            'solicitudviaje',
            'solicitudpagodirecto',
            'rendicioncuentas',
            'informeactividadprincipal',
            'informetareaprincipal',
        ]
        
        content_types = ContentType.objects.filter(
            model__in=modelos_necesarios
        ).values('model', 'id')
        
        return {
            ct['model']: ct['id'] 
            for ct in content_types
        }
    
    def _generar_resumen_proyecto(
        self,
        proyecto,
        content_types: Dict[str, int],
        adjuntos_data: Dict[str, List[str]],
        referencias_data: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Genera resumen usando datos precargados.
        No hace queries adicionales.
        """
        conteo = {
            'documentos': 0,
            'imagenes': 0,
            'videos': 0,
            'audios': 0,
            'otros': 0,
        }
        
        total_adjuntos = 0
        total_referencias = 0
        
        # Obtener todos los objetos del proyecto (ya tenemos los IDs)
        objetos_relacionados = self._get_objetos_relacionados(proyecto.id)
        
        # Contar adjuntos y referencias para cada objeto
        for obj in objetos_relacionados:
            modelo_name = obj.__class__.__name__.lower()
            ct_id = content_types.get(modelo_name)
            
            if ct_id:
                key = f"{ct_id}:{obj.id}"
                
                # Adjuntos
                if key in adjuntos_data:
                    for tipo in adjuntos_data[key]:
                        clave = self.TIPO_MAPEO.get(tipo, 'otros')
                        conteo[clave] += 1
                        total_adjuntos += 1
                
                # Referencias
                if key in referencias_data:
                    total_referencias += referencias_data[key]
        
        return {
            'id': proyecto.id,
            'nombre': proyecto.titulo,
            'codigo': proyecto.codigo,
            'descripcion': proyecto.descripcion or '',
            'estado': proyecto.estado,
            'fecha_creacion': proyecto.fecha_creacion.date(),
            'fecha_actualizacion': proyecto.fecha_creacion.date(),
            'propietario': proyecto.propietario_id,
            'instancias_gestoras': [
                {
                    'id': ig.id,
                    'codigo': ig.codigo or '',
                    'clasificador': ig.clasificador or '',
                    'instancia': ig.instancia,
                }
                for ig in proyecto.instancia_gestora.all()
            ],
            'totalArchivos': total_adjuntos,
            'totalReferencias': total_referencias,
            'conteoArchivos': conteo,
        }
    
    def _get_objetos_relacionados(self, proyecto_id: int) -> List[Any]:
        """
        Obtiene todos los objetos relacionados al proyecto.
        Usa queries masivas (una por modelo).
        """
        objetos = []
        
        # Objetivos generales
        ogs = ObjetivoGeneralProyecto.objects.filter(proyecto_id=proyecto_id)
        objetos.extend(ogs)
        
        og_ids = [og.id for og in ogs]
        
        if og_ids:
            # Indicadores OG
            objetos.extend(IndicadorObjetivoGeneral.objects.filter(
                objetivo_general_id__in=og_ids
            ))
            
            # Resultados OG
            rogs = ResultadoOG.objects.filter(objetivo_general_id__in=og_ids)
            objetos.extend(rogs)
            
            rog_ids = [rog.id for rog in rogs]
            if rog_ids:
                objetos.extend(IndicadorResultadoObjGral.objects.filter(
                    resultado_og_id__in=rog_ids
                ))
            
            # Objetivos específicos
            oes = ObjetivoEspecificoProyecto.objects.filter(
                objetivo_general_id__in=og_ids
            )
            objetos.extend(oes)
            
            oe_ids = [oe.id for oe in oes]
            if oe_ids:
                objetos.extend(IndicadorObjetivoEspecifico.objects.filter(
                    objetivo_especifico_id__in=oe_ids
                ))
                
                roes = ResultadoOE.objects.filter(
                    objetivo_especifico_id__in=oe_ids
                )
                objetos.extend(roes)
                
                roe_ids = [roe.id for roe in roes]
                if roe_ids:
                    objetos.extend(IndicadorResultadoObjEspecifico.objects.filter(
                        resultado_obj_especifico_id__in=roe_ids
                    ))
        
        # Actividades
        actividades = Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False,
        )
        objetos.extend(actividades)
        
        act_ids = [act.id for act in actividades]
        
        if act_ids:
            # Tareas
            tareas = TareaActividad.objects.filter(actividad_id__in=act_ids)
            objetos.extend(tareas)
            
            tarea_ids = [t.id for t in tareas]
            
            # Solicitudes
            objetos.extend(SolicitudFondos.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ))
            objetos.extend(SolicitudReembolso.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ))
            objetos.extend(SolicitudViaje.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ))
            objetos.extend(SolicitudPagoDirecto.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ))
            
            # Rendiciones
            objetos.extend(RendicionCuentas.objects.filter(
                Q(actividad_id__in=act_ids) | Q(tarea_id__in=tarea_ids)
            ))
            
            # Informes
            objetos.extend(InformeActividadPrincipal.objects.filter(
                actividad_id__in=act_ids
            ))
            
            if tarea_ids:
                objetos.extend(InformeTareaPrincipal.objects.filter(
                    tarea_id__in=tarea_ids
                ))
        
        return objetos
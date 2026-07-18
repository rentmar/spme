# spme/spme_validaciones/services/solicitudes_pago_directo_usuario_service.py
# services/solicitudes_pago_directo_usuario_service.py
from typing import Dict, List, Any, Optional
import logging

from ..repositories.solicitudes_pago_directo_usuario_repository import (
    SolicitudesPagoDirectoUsuarioRepository
)

logger = logging.getLogger(__name__)


class SolicitudesPagoDirectoUsuarioService:
    """
    Servicio de lógica de negocio especializado en Solicitudes de Pago Directo.
    """
    
    ROL_REDACTOR = 'REDACTOR'
    ROL_REVISOR = 'REVISOR'
    ROL_REDACTOR_REVISOR = 'REDACTOR_REVISOR'
    ROL_SIN_ROL = 'SIN_ROL'
    
    ESTADO_APROBADO = 'Aprobado'
    ESTADO_RECHAZADO = 'Rechazado'
    ESTADO_PENDIENTE = 'Pendiente'
    ESTADO_SIN_REVISORES = 'SinRevisores'
    
    def __init__(self, repository: Optional[SolicitudesPagoDirectoUsuarioRepository] = None):
        self.repository = repository or SolicitudesPagoDirectoUsuarioRepository()
    
    def obtener_solicitudes_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """Método principal que orquesta la obtención y estructuración de datos."""
        try:
            solicitudes = self.repository.obtener_solicitudes_por_usuario(usuario_id)
            
            solicitudes_procesadas = []
            contadores = {
                'como_redactor': 0,
                'como_revisor': 0,
                'como_redactor_revisor': 0,
                'pendientes_revision': 0,
                'aprobadas': 0,
                'rechazadas': 0,
                'sin_revision': 0
            }
            
            for solicitud in solicitudes:
                try:
                    registro = self._procesar_solicitud(solicitud, usuario_id)
                    solicitudes_procesadas.append(registro)
                    self._actualizar_contadores(registro, contadores)
                except Exception as e:
                    logger.error(
                        f"Error procesando solicitud pago directo {solicitud.id}: {str(e)}",
                        exc_info=True
                    )
                    continue
            
            return self._construir_respuesta(solicitudes_procesadas, contadores)
            
        except Exception as e:
            logger.error(
                f"Error obteniendo solicitudes pago directo para usuario {usuario_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    def _procesar_solicitud(self, solicitud, usuario_id: int) -> Dict[str, Any]:
        """Procesa una solicitud individual aplicando reglas de negocio."""
        validaciones = solicitud.validaciones.all()
        
        es_redactor = self._es_usuario_redactor(usuario_id, validaciones)
        es_revisor = self._es_usuario_revisor(usuario_id, validaciones)
        le_pertenece = (solicitud.usuario_id == usuario_id)
        rol = self._determinar_rol(es_redactor, es_revisor, le_pertenece)
        
        estado_consolidado = self._calcular_estado_consolidado(validaciones)
        
        datos_mi_validacion = self._obtener_datos_mi_validacion(
            usuario_id, validaciones, es_revisor
        )
        
        versiones_como_redactor = self._obtener_versiones_como_redactor(
            usuario_id, validaciones, es_redactor
        )
        
        stats = self.repository.obtener_estadisticas_validaciones(solicitud.id)
        
        revisores = self._construir_info_revisores(validaciones, usuario_id)
        
        info_actividad = self._construir_info_actividad(solicitud)
        info_tarea = self._construir_info_tarea(solicitud)
        
        return self._construir_registro_solicitud(
            solicitud=solicitud,
            le_pertenece=le_pertenece,
            rol=rol,
            es_redactor=es_redactor,
            es_revisor=es_revisor,
            estado_consolidado=estado_consolidado,
            datos_mi_validacion=datos_mi_validacion,
            versiones_como_redactor=versiones_como_redactor,
            stats=stats,
            revisores=revisores,
            actividad=info_actividad,
            tarea=info_tarea
        )
    
    def _es_usuario_redactor(self, usuario_id: int, validaciones) -> bool:
        return any(v.usuarioRedactor_id == usuario_id for v in validaciones)
    
    def _es_usuario_revisor(self, usuario_id: int, validaciones) -> bool:
        return any(v.usuarioValidador_id == usuario_id for v in validaciones)
    
    def _determinar_rol(self, es_redactor: bool, es_revisor: bool, le_pertenece: bool) -> str:
        if es_redactor and es_revisor:
            return self.ROL_REDACTOR_REVISOR
        elif es_redactor:
            return self.ROL_REDACTOR
        elif es_revisor:
            return self.ROL_REVISOR
        return self.ROL_SIN_ROL
    
    def _calcular_estado_consolidado(self, validaciones) -> str:
        if not validaciones:
            return self.ESTADO_SIN_REVISORES
        
        estados = [v.estado for v in validaciones]
        
        if 'RECHAZADO' in estados:
            return self.ESTADO_RECHAZADO
        
        if all(estado == 'APROBADO' for estado in estados):
            return self.ESTADO_APROBADO
        
        return self.ESTADO_PENDIENTE
    
    def _obtener_datos_mi_validacion(self, usuario_id: int, validaciones, es_revisor: bool) -> Dict:
        if not es_revisor:
            return {
                'estado': None,
                'versionDocumento': None,
                'fechaAsignacion': None,
                'fechaResolucion': None,
                'pendiente': False
            }
        
        for v in validaciones:
            if v.usuarioValidador_id == usuario_id:
                return {
                    'estado': v.estado,
                    'versionDocumento': v.versionDocumento,
                    'fechaAsignacion': v.fechaAsignacion,
                    'fechaResolucion': v.fechaResolucion,
                    'pendiente': v.estado == 'PENDIENTE'
                }
        
        return {
            'estado': None,
            'versionDocumento': None,
            'fechaAsignacion': None,
            'fechaResolucion': None,
            'pendiente': False
        }
    
    def _obtener_versiones_como_redactor(self, usuario_id: int, validaciones, es_redactor: bool) -> List[str]:
        if not es_redactor:
            return []
        
        versiones = []
        for v in validaciones:
            if v.usuarioRedactor_id == usuario_id:
                versiones.append(v.versionDocumento)
        return versiones
    
    def _construir_info_revisores(self, validaciones, usuario_id: int) -> List[Dict]:
        revisores = []
        for validacion in validaciones:
            revisor = {
                'id': validacion.usuarioValidador_id,
                'nombre': validacion.usuarioValidador.get_full_name() 
                          if validacion.usuarioValidador else None,
                'estado': validacion.estado,
                'fechaAsignacion': validacion.fechaAsignacion,
                'fechaResolucion': validacion.fechaResolucion,
                'versionDocumento': validacion.versionDocumento,
                'comentarios': validacion.comentarios or '',
                'codigoSeguimiento': validacion.codigoSeguimiento,
                'esRedactor': validacion.usuarioRedactor_id == validacion.usuarioValidador_id,
                'esUsuarioActual': validacion.usuarioValidador_id == usuario_id
            }
            revisores.append(revisor)
        return revisores
    
    def _construir_info_actividad(self, solicitud) -> Optional[Dict]:
        if not solicitud.actividad_id:
            return None
        
        actividad = solicitud.actividad
        
        data = {
            'id': actividad.id,
            'codigo': actividad.codigo or '',
            'nombre': actividad.nombreCorto or '',
            'descripcion': actividad.descripcion or '',
            'estado': actividad.estado or '',
            'estadoDisplay': self._get_estado_actividad_display(actividad.estado),
            'tipo': None,
            'fechaInicio': actividad.fecha_inicio,
            'fechaCierre': actividad.fecha_cierre,
            'presupuesto': float(actividad.presupuesto) if actividad.presupuesto else None,
            'responsable': None,
            'proyecto': None
        }
        
        if actividad.tipo:
            data['tipo'] = {
                'id': actividad.tipo_id,
                'sigla': actividad.tipo.sigla,
                'tipo': actividad.tipo.tipo_actividad
            }
        
        if actividad.responsable:
            data['responsable'] = {
                'id': actividad.responsable_id,
                'nombre': actividad.responsable.get_full_name()
            }
        
        if actividad.proyecto:
            data['proyecto'] = {
                'id': actividad.proyecto_id,
                'codigo': getattr(actividad.proyecto, 'codigo', None),
                'nombre': getattr(actividad.proyecto, 'nombre', str(actividad.proyecto))
            }
        
        return data
    
    def _construir_info_tarea(self, solicitud) -> Optional[Dict]:
        if not solicitud.tarea_id:
            return None
        
        tarea = solicitud.tarea
        
        return {
            'id': tarea.id,
            'codigo': tarea.codigo or '',
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.estado or '',
            'estadoDisplay': self._get_estado_tarea_display(tarea.estado),
            'fechaEjecucion': tarea.fecha_ejecucion,
            'fechaLimite': tarea.fecha_limite,
            'presupuesto': float(tarea.presupuesto) if tarea.presupuesto else None
        }
    
    def _get_estado_actividad_display(self, estado: str) -> str:
        mapping = {
            'CRD': 'Creada',
            'PLAN': 'Planificada',
            'RETR': 'Retraso',
            'REPROG': 'Reprogramacion',
            'EJEC': 'En Ejecucion',
            'REP': 'En Reporte',
            'FIN': 'Finalizado',
        }
        return mapping.get(estado, estado)
    
    def _get_estado_tarea_display(self, estado: str) -> str:
        mapping = {
            'PEN': 'Pendiente',
            'EPROG': 'En Progreso',
            'COMPL': 'Completada',
        }
        return mapping.get(estado, estado)
    
    def _construir_registro_solicitud(
        self,
        solicitud,
        le_pertenece: bool,
        rol: str,
        es_redactor: bool,
        es_revisor: bool,
        estado_consolidado: str,
        datos_mi_validacion: Dict,
        versiones_como_redactor: List[str],
        stats: Dict,
        revisores: List[Dict],
        actividad: Optional[Dict],
        tarea: Optional[Dict]
    ) -> Dict[str, Any]:
        """Construye el registro unificado para una solicitud de pago directo."""
        return {
            # Identificación
            'id': solicitud.id,
            'numeroForm': solicitud.numeroFormulario,
            'tipoDocumento': 'Solicitud de Pago Directo',
            'subtipo': solicitud.subtipo_display,
            
            # Datos específicos de Pago Directo
            'descripcionActividad': solicitud.descripcion_actividad or '',
            'objetivoActividad': solicitud.objetivo_actividad or '',
            'fechaRealizacionActividad': solicitud.fechaRealizacionActividad,
            
            # Actividad y Tarea
            'actividad': actividad,
            'tarea': tarea,
            
            # Datos generales
            'lugarSolicitud': solicitud.lugarSolicitud or '',
            'fechaSolicitud': solicitud.fechaSolicitud,
            'montoSolicitado': float(solicitud.montoSolicitado) if solicitud.montoSolicitado else 0,
            
            # Pertenencia y roles
            'lePertenece': le_pertenece,
            'rolUsuario': rol,
            'esRedactor': es_redactor,
            'esRevisor': es_revisor,
            'pendienteRevision': datos_mi_validacion['pendiente'],
            
            # Estados
            'estadoConsolidado': estado_consolidado,
            'estadoMiValidacion': datos_mi_validacion['estado'],
            
            # Versiones
            'miVersionDocumento': datos_mi_validacion['versionDocumento'],
            'versionesComoRedactor': versiones_como_redactor,
            
            # Estadísticas
            'totalRevisores': stats['total'],
            'revisoresQueAprobaron': stats['aprobadas'],
            'revisoresQueRechazaron': stats['rechazadas'],
            'revisoresPendientes': stats['pendientes'],
            
            # Fechas
            'fechaAsignacion': datos_mi_validacion['fechaAsignacion'],
            'fechaResolucion': datos_mi_validacion['fechaResolucion'],
            
            # Revisores
            'revisores': revisores,
            
            # Dueño
            'usuarioSolicitante': {
                'id': solicitud.usuario_id,
                'nombre': solicitud.usuario.get_full_name() if solicitud.usuario else None,
            },
            
            # URLs
            'url': solicitud.get_accion_url(),
            'urlAccion': solicitud.get_accion_url_texto(),
        }
    
    def _actualizar_contadores(self, registro: Dict, contadores: Dict) -> None:
        if registro['esRedactor']:
            contadores['como_redactor'] += 1
        if registro['esRevisor']:
            contadores['como_revisor'] += 1
        if registro['rolUsuario'] == self.ROL_REDACTOR_REVISOR:
            contadores['como_redactor_revisor'] += 1
        if registro['pendienteRevision']:
            contadores['pendientes_revision'] += 1
        if registro['estadoConsolidado'] == self.ESTADO_APROBADO:
            contadores['aprobadas'] += 1
        elif registro['estadoConsolidado'] == self.ESTADO_RECHAZADO:
            contadores['rechazadas'] += 1
        elif registro['estadoConsolidado'] == self.ESTADO_SIN_REVISORES:
            contadores['sin_revision'] += 1
    
    def _construir_respuesta(self, solicitudes: List[Dict], contadores: Dict) -> Dict[str, Any]:
        return {
            'tipo': 'solicitudes_pago_directo',
            'total': len(solicitudes),
            'solicitudes': solicitudes,
            'resumen': {
                'totalSolicitudes': len(solicitudes),
                'comoRedactor': contadores['como_redactor'],
                'comoRevisor': contadores['como_revisor'],
                'comoRedactorRevisor': contadores['como_redactor_revisor'],
                'pendientesRevision': contadores['pendientes_revision'],
                'aprobadas': contadores['aprobadas'],
                'rechazadas': contadores['rechazadas'],
                'sinRevision': contadores['sin_revision']
            }
        }
    
    def obtener_pendientes_revision(self, usuario_id: int) -> List[Dict]:
        """
        Obtiene validaciones pendientes para pagos directos.
        """
        try:
            validaciones = self.repository.obtener_validaciones_pendientes_por_usuario(usuario_id)
            
            pendientes = []
            for v in validaciones:
                solicitud = v.solicitud
                pendientes.append({
                    'validacionId': v.id,
                    'codigoSeguimiento': v.codigoSeguimiento,
                    'estado': v.estado,
                    'fechaAsignacion': v.fechaAsignacion,
                    'versionDocumento': v.versionDocumento,
                    'solicitudId': solicitud.id,
                    'solicitudCodigo': solicitud.numeroFormulario or f"SPD-{solicitud.id}",
                    'solicitudMonto': float(solicitud.montoSolicitado) if solicitud.montoSolicitado else 0,
                    'tipoDocumento': 'Solicitud de Pago Directo',
                    'subtipo': solicitud.subtipo_display,
                    'solicitanteNombre': v.usuarioRedactor.get_full_name() if v.usuarioRedactor else 'N/A',
                    'solicitudUrl': solicitud.get_accion_url(),
                    'solicitudUrlTexto': solicitud.get_accion_url_texto(),
                })
            
            return pendientes
            
        except Exception as e:
            logger.error(f"Error pendientes pagos usuario {usuario_id}: {str(e)}", exc_info=True)
            return []
        

    def obtener_validaciones_como_validador(self, usuario_id: int) -> List[Dict]:
        """
        Obtiene TODAS las validaciones de pagos directos donde el usuario es validador.
        
        Incluye todos los estados: PENDIENTE, APROBADO, RECHAZADO
        
        Args:
            usuario_id: ID del usuario validador
            
        Returns:
            Lista de validaciones con datos de la solicitud
        """
        try:
            validaciones = self.repository.obtener_validaciones_por_validador(usuario_id)
            
            datos = []
            for v in validaciones:
                solicitud = v.solicitud
                datos.append({
                    'validacionId': v.id,
                    'codigoSeguimiento': v.codigoSeguimiento,
                    'estado': v.estado,
                    'fechaAsignacion': v.fechaAsignacion,
                    'fechaResolucion': v.fechaResolucion,
                    'versionDocumento': v.versionDocumento,
                    'comentarios': v.comentarios or '',
                    'solicitudId': solicitud.id,
                    'solicitudCodigo': solicitud.numeroFormulario or f"SPD-{solicitud.id}",
                    'solicitudMonto': float(solicitud.montoSolicitado) if solicitud.montoSolicitado else 0,
                    'tipoDocumento': 'Solicitud de Pago Directo',
                    'subtipo': solicitud.subtipo_display,
                    'solicitanteId': solicitud.usuario_id,
                    'solicitanteNombre': solicitud.usuario.get_full_name() if solicitud.usuario else 'N/A',
                    'solicitudUrl': solicitud.get_accion_url(),
                    'solicitudUrlTexto': solicitud.get_accion_url_texto(),
                })
            
            return datos
            
        except Exception as e:
            logger.error(f"Error validaciones pagos usuario {usuario_id}: {str(e)}", exc_info=True)
            return []

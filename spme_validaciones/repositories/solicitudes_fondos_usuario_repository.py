#spme/spme_validaciones/repositories/solicitudes_fondos_usuario_repository.py
from django.db.models import Q, Prefetch, QuerySet
from typing import Dict, Optional
from ..models import ValidacionSolicitudFondos
from spme_monitoreo.models import SolicitudFondos

class SolicitudesFondosUsuarioRepository:
    """
    Repositorio especializado para consultas de Solicitudes de Fondos.
    
    Responsabilidades:
    - Acceso a datos exclusivo para SolicitudFondos y ValidacionSolicitudFondos
    - Construcción de querysets optimizados con prefetch_related
    - No contiene lógica de negocio
    
    Patrón: Repository Pattern
    """

    def obtener_solicitudes_por_usuario(self, usuario_id: int) -> QuerySet:
        """
        Obtiene todas las solicitudes de fondos donde el usuario está involucrado.
        
        Criterios de filtrado (OR):
        1. La solicitud le pertenece: solicitud.usuario_id == usuario_id
        2. Es REDACTOR: existe validación con usuarioRedactor_id == usuario_id
        3. Es REVISOR: existe validación con usuarioValidador_id == usuario_id
        
        Args:
            usuario_id: ID del usuario autenticado
            
        Returns:
            QuerySet con solicitudes únicas, ordenadas por fecha descendente,
            con validaciones y usuarios relacionados precargados
        """
        return (
        SolicitudFondos.objects
        .filter(
            Q(usuario_id=usuario_id) |
            Q(validaciones__usuarioRedactor_id=usuario_id) |
            Q(validaciones__usuarioValidador_id=usuario_id)
        )
        .distinct()
        .select_related(
            'usuario',
            'actividad',
            'actividad__tipo',
            'actividad__responsable',
            'actividad__proyecto',
            'tarea'
        )
        .prefetch_related(
            Prefetch(
                'validaciones',
                queryset=ValidacionSolicitudFondos.objects.select_related(
                    'usuarioValidador',
                    'usuarioRedactor'
                ).order_by('-fechaAsignacion')
            )
        )
        .order_by('-fechaSolicitud')
    )
        
    
    def obtener_estadisticas_validaciones(self, solicitud_id: int) -> Dict:
        """
        Obtiene estadísticas agregadas de validaciones para una solicitud.
        
        Args:
            solicitud_id: ID de la solicitud
            
        Returns:
            Diccionario con conteos:
            {
                'total': 3,
                'aprobadas': 2,
                'rechazadas': 0,
                'pendientes': 1
            }
        """

        validaciones = ValidacionSolicitudFondos.objects.filter(
            solicitud_id=solicitud_id
        )

        total = validaciones.count()

        if total == 0:
            return {
                'total': 0,
                'aprobadas': 0,
                'rechazadas': 0,
                'pendientes': 0
            }
        
        return {
            'total': total,
            'aprobadas': validaciones.filter(estado='APROBADO').count(),
            'rechazadas': validaciones.filter(estado='RECHAZADO').count(),
            'pendientes': validaciones.filter(estado='PENDIENTE').count(),
        }
    
    def obtener_validaciones_pendientes_por_usuario(self, usuario_id: int) -> QuerySet:
        """
        Obtiene las validaciones pendientes del usuario para solicitudes de fondos.

        Args:
            usuario_id: ID del usuario revisor
        
        Returns:
            QuerySet de ValidacionSolicitudFondos filtrado por:
            - usuarioValidador_id = usuario_id
            - estado = 'PENDIENTE'
        """
        return(
            ValidacionSolicitudFondos.objects
            .filter(
                usuarioValidador_id=usuario_id,
                estado='PENDIENTE'
            )
            .select_related(
                'solicitud',
                'solicitud__usuario',
                'usuarioRedactor'
            )
            .order_by('-fechaAsignacion')
        )



# spme/spme_validaciones/repositories/solicitudes_reembolso_usuario_repository.py
from django.db.models import Q, Prefetch, QuerySet
from typing import Dict
from ..models import ValidacionSolicitudReembolso
from spme_monitoreo.models import SolicitudReembolso


class SolicitudesReembolsoUsuarioRepository:
    """
    Repositorio especializado para consultas de Solicitudes de Reembolso.
    """
    
    def obtener_solicitudes_por_usuario(self, usuario_id: int) -> QuerySet:
        """
        Obtiene todas las solicitudes de reembolso donde el usuario está involucrado.
        
        Criterios de filtrado (OR):
        1. La solicitud le pertenece: solicitud.usuario_id == usuario_id
        2. Es REDACTOR: existe validación con usuarioRedactor_id == usuario_id
        3. Es REVISOR: existe validación con usuarioValidador_id == usuario_id
        """
        return (
            SolicitudReembolso.objects
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
                    queryset=ValidacionSolicitudReembolso.objects.select_related(
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
        """
        validaciones = ValidacionSolicitudReembolso.objects.filter(
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
        Validaciones pendientes para reembolsos.
        """
        return (
            ValidacionSolicitudReembolso.objects
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
    
    def obtener_validaciones_por_validador(self, usuario_id: int) -> QuerySet:
        """Obtiene TODAS las validaciones donde el usuario es validador para reembolsos."""
        return (
            ValidacionSolicitudReembolso.objects
            .filter(usuarioValidador_id=usuario_id)
            .select_related(
                'solicitud',
                'solicitud__usuario',
                'solicitud__actividad',
                'solicitud__tarea',
                'usuarioRedactor'
            )
            .order_by('-fechaAsignacion')
        )
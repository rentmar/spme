# repositories/rendicion_cuentas_usuario_repository.py

from django.db.models import Q, Prefetch, QuerySet
from typing import Dict
from ..models import ValidacionRendicionCuentas
from spme_monitoreo.models import RendicionCuentas


class RendicionCuentasUsuarioRepository:
    """
    Repositorio especializado para consultas de Rendición de Cuentas.
    """
    
    def obtener_solicitudes_por_usuario(self, usuario_id: int) -> QuerySet:
        """
        Obtiene todas las rendiciones de cuentas donde el usuario está involucrado.
        """
        return (
            RendicionCuentas.objects
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
                'tarea',
                'solicitudFondos',
                'solicitudReembolso',
                'solicitudViaje',
                'solicitudPagoDirecto'
            )
            .prefetch_related(
                Prefetch(
                    'validaciones',
                    queryset=ValidacionRendicionCuentas.objects.select_related(
                        'usuarioValidador',
                        'usuarioRedactor'
                    ).order_by('-fechaAsignacion')
                )
            )
            .order_by('-fechaRendicion')
        )
    
    def obtener_estadisticas_validaciones(self, rendicion_id: int) -> Dict:
        """
        Obtiene estadísticas agregadas de validaciones para una rendición.
        
        Args:
            rendicion_id: ID de la rendición de cuentas
            
        Returns:
            Diccionario con conteos de validaciones por estado
        """
        validaciones = ValidacionRendicionCuentas.objects.filter(
            rendicion_id=rendicion_id  # ✅ CORREGIDO: rendicion_id en vez de solicitud_id
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
        Validaciones pendientes para rendiciones de cuentas.
        """
        return (
            ValidacionRendicionCuentas.objects
            .filter(
                usuarioValidador_id=usuario_id,
                estado='PENDIENTE'
            )
            .select_related(
                'rendicion',
                'rendicion__usuario',
                'usuarioRedactor'
            )
            .order_by('-fechaAsignacion')
        )
    
    def obtener_validaciones_por_validador(self, usuario_id: int) -> QuerySet:
        """Obtiene TODAS las validaciones donde el usuario es validador para rendiciones."""
        return (
            ValidacionRendicionCuentas.objects
            .filter(usuarioValidador_id=usuario_id)
            .select_related(
                'rendicion',
                'rendicion__usuario',
                'rendicion__actividad',
                'rendicion__tarea',
                'usuarioRedactor'
            )
            .order_by('-fechaAsignacion')
        )
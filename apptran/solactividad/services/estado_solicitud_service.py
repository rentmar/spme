# spme_monitoreo/services/estado_solicitud_service.py 
from django.db.models import QuerySet, Q, Count, F
from collections import Counter
#Servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion


class EstadoSolicitudService:
    """
    Servicio para determinar el estado consolidado de solicitudes
    basado en el sistema de validaciones (ValidacionSolicitudFondos).
    
    Estados:
    - sin_revisores: No tiene validaciones asignadas
    - pendiente:     Al menos una validación PENDIENTE, ninguna RECHAZADA
    - aprobada:      Todas las validaciones APROBADO
    - rechazada:     Al menos una validación RECHAZADA
    """
    
    @staticmethod
    def get_estado_actual(solicitud) -> str:
        """Retorna el estado consolidado de una solicitud individual."""
        # validaciones = solicitud.validaciones.all()
        
        # if not validaciones.exists():
        #     return 'sin_revisores'
        
        # estados = set(validaciones.values_list('estado', flat=True))
        
        # if 'RECHAZADO' in estados:
        #     return 'rechazada'
        
        # if estados == {'APROBADO'}:
        #     return 'aprobada'
        
        # if 'PENDIENTE' in estados:
        #     return 'pendiente'
        
        # return 'pendiente'
        validaciones_memoria = list(solicitud.validaciones.all())
        service = ConsolidacionValidacionService()
        
        return service.consolidar_desde_validaciones(
            tipo_solicitud="SOLICITUD_FONDOS",
            validaciones=validaciones_memoria,
            metodo_resolucion=MetodoResolucion.DECISORIO,
        )
    
    @staticmethod
    def get_estado_display(estado: str) -> str:
        """Convierte el estado interno a formato legible para el frontend."""
        mapping = {
            'sin_revisores': 'SinRevisores',
            'pendiente': 'Pendiente',
            'aprobada': 'Aprobado',
            'rechazada': 'Rechazado',
        }
        return mapping.get(estado, estado)
    
    @staticmethod
    def filtrar_por_estado(queryset: QuerySet, estado: str) -> QuerySet:
        """Filtra un queryset por estado consolidado."""
        estado_lower = estado.lower()

        if estado_lower == 'sin_revisores':
            return queryset.annotate(total=Count('validaciones')).filter(total=0)
        
        elif estado_lower == ['rechazado', 'rechazada']:
            return queryset.annotate(
                rechazadas=Count('validaciones', filter=Q(validaciones__estado='RECHAZADO'))
            ).filter(rechazadas__gt=0)
        
        elif estado_lower == ['aprobado', 'aprobada']:
            return queryset.annotate(
                total=Count('validaciones'),
                aprobadas=Count('validaciones', filter=Q(validaciones__estado='APROBADO')),
                rechazadas=Count('validaciones', filter=Q(validaciones__estado='RECHAZADO')),
            ).filter(total__gt=0, aprobadas=F('total'), rechazadas=0)
        
        elif estado_lower == 'pendiente':
            return queryset.annotate(
                total=Count('validaciones'),
                pendientes=Count('validaciones', filter=Q(validaciones__estado='PENDIENTE')),
                rechazadas=Count('validaciones', filter=Q(validaciones__estado='RECHAZADO')),
            ).filter(total__gt=0, pendientes__gt=0, rechazadas=0)
        
        return queryset
    
    @staticmethod
    def get_estadisticas(queryset: QuerySet) -> dict:
        """Calcula estadísticas de estados para un queryset."""
        total = queryset.count()
        if total == 0:
            return {
                'total': 0,
                'sin_revisores': 0,
                'pendientes': 0,
                'aprobadas': 0,
                'rechazadas': 0,
            }
        
        estados_counter = Counter()
        service = ConsolidacionValidacionService()
        
        # for solicitud in queryset.prefetch_related('validaciones'):
        #     estado = EstadoSolicitudService.get_estado_actual(solicitud)
        #     estados_counter[estado] += 1

        for solicitud in queryset.prefetch_related('validaciones'):
            validaciones_memoria = list(solicitud.validaciones.all())
            estado = service.consolidar_desde_validaciones(
                tipo_solicitud="SOLICITUD_FONDOS",
                validaciones=validaciones_memoria,
                metodo_resolucion=MetodoResolucion.TODO_O_NADA
            )
            estados_counter[estado] += 1
        
        
        return {
            'total': total,
            'sin_revisores': estados_counter.get('SIN_VALIDACIONES', 0),
            'pendientes': estados_counter.get('PENDIENTE', 0),
            'aprobadas': estados_counter.get('APROBADO', 0),
            'rechazadas': estados_counter.get('RECHAZADO', 0),
        }
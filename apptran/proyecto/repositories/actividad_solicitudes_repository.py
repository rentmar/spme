# api/v2/repositories/actividad_solicitudes_repository.py

from django.db.models import Q
from spme_actividades.models import Actividad
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudReembolso,
)


class ActividadSolicitudesRepository:
    """Repositorio para actividades con información de solicitudes."""

    @staticmethod
    def get_actividades_con_tareas(usuario, filtros=None):
        """Obtiene actividades con tareas relacionadas."""
        queryset = Actividad.objects.select_related(
            'responsable', 'proyecto'
        ).prefetch_related(
            'tareas'
        ).filter(
            estaInactiva=False
        ).exclude(
            estado='CRD'
        )

        if hasattr(usuario, 'rol'):
            if usuario.rol == 'coordinador':
                queryset = queryset.filter(
                    proyecto__coordinacion_id=usuario.coordinacion_id
                )
            elif usuario.rol == 'responsable':
                queryset = queryset.filter(responsable_id=usuario.id)

        if filtros:
            if filtros.get('search'):
                query = filtros['search'].lower()
                queryset = queryset.filter(
                    Q(codigo__icontains=query) |
                    Q(nombreCorto__icontains=query)
                )
            if filtros.get('estado'):
                estados = filtros['estado'].split(',')
                queryset = queryset.filter(estado__in=estados)

        return queryset.order_by('-id')

    @staticmethod
    def get_badges_actividad(actividad_id):
        """Calcula los badges para una actividad (solo solicitudes sin tarea)."""
        return {
            'fondos': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudFondos, actividad_id=actividad_id, tarea__isnull=True
            ),
            'viajes': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudViaje, actividad_id=actividad_id, tarea__isnull=True
            ),
            'pagos_directos': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudPagoDirecto, actividad_id=actividad_id, tarea__isnull=True
            ),
            'reposiciones': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudReembolso, actividad_id=actividad_id, tarea__isnull=True
            ),
        }

    @staticmethod
    def get_badges_tarea(tarea_id):
        """Calcula los badges para una tarea."""
        return {
            'fondos': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudFondos, tarea_id=tarea_id
            ),
            'viajes': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudViaje, tarea_id=tarea_id
            ),
            'pagos_directos': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudPagoDirecto, tarea_id=tarea_id
            ),
            'reposiciones': ActividadSolicitudesRepository._contar_con_validaciones(
                SolicitudReembolso, tarea_id=tarea_id
            ),
        }

    @staticmethod
    def _contar_con_validaciones(modelo, **filtros):
        """
        Cuenta solicitudes usando los modelos de validación.
        
        Retorna:
        - creadas: total de solicitudes (con y sin revisores)
        - aprobadas: todas las validaciones en APROBADO
        - rechazadas: alguna validación en RECHAZADO
        - pendientes: alguna validación en PENDIENTE (tiene revisores pero no todos aprobaron)
        - borradores: sin revisores asignados
        """
        solicitudes = modelo.objects.filter(**filtros)

        creadas = solicitudes.count()
        aprobadas = 0
        rechazadas = 0
        pendientes = 0
        borradores = 0

        for solicitud in solicitudes:
            validaciones = solicitud.validaciones.all()

            if not validaciones.exists():
                borradores += 1
                continue

            estados = set(validaciones.values_list('estado', flat=True))

            if 'RECHAZADO' in estados:
                rechazadas += 1
            elif estados == {'APROBADO'}:
                aprobadas += 1
            else:
                pendientes += 1

        return {
            'creadas': creadas,
            'aprobadas': aprobadas,
            'rechazadas': rechazadas,
            'pendientes': pendientes,
            'borradores': borradores,
        }
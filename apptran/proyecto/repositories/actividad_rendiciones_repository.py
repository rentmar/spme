from django.db.models import Q
from spme_actividades.models import Actividad
from spme_monitoreo.models import RendicionCuentas

class ActividadRendicionesRepository:

    @staticmethod
    def get_actividades_con_tareas(usuario, filtros=None):
        queryset = Actividad.objects.select_related(
            'responsable', 'proyecto'
        ).prefetch_related(
            'tareas'
        ).filter(estaInactiva=False).exclude(estado='CRD')

        if filtros:
            if filtros.get('search'):
                query = filtros['search'].lower()
                queryset = queryset.filter(
                    Q(codigo__icontains=query) | Q(nombreCorto__icontains=query)
                )
            if filtros.get('estado'):
                estados = filtros['estado'].split(',')
                queryset = queryset.filter(estado__in=estados)

        return queryset.order_by('-id')

    @staticmethod
    def get_badges_actividad(actividad_id):
        return {
            'rendiciones': ActividadRendicionesRepository._contar_rendiciones(
                RendicionCuentas, actividad_id=actividad_id, tarea__isnull=True
            ),
        }

    @staticmethod
    def get_badges_tarea(tarea_id):
        return {
            'rendiciones': ActividadRendicionesRepository._contar_rendiciones(
                RendicionCuentas, tarea_id=tarea_id
            ),
        }

    @staticmethod
    def _contar_rendiciones(modelo, **filtros):
        rendiciones = modelo.objects.filter(**filtros)
        creadas = rendiciones.count()
        aprobadas = 0
        rechazadas = 0
        pendientes = 0
        borradores = 0

        for rendicion in rendiciones:
            validaciones = rendicion.validaciones.all()
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
    
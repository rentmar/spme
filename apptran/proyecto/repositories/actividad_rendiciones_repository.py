# spme/apptran/proyecto/repositories/actividad_rendiciones_repository.py
from django.db.models import Q
from spme_actividades.models import Actividad
from spme_monitoreo.models import RendicionCuentas

#Servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion

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
        #1) Precargar las validaciones en memoria
        rendiciones = modelo.objects.filter(**filtros).prefetch_related('validaciones')

        # rendiciones = modelo.objects.filter(**filtros)
        creadas = rendiciones.count()
        aprobadas = 0
        rechazadas = 0
        pendientes = 0
        borradores = 0

        #2) Instanciamos el servicio de consolidacion
        service = ConsolidacionValidacionService()

        #3) Iteramos las rendiciones precargadas
        for rendicion in rendiciones:
            validaciones_memoria = list(rendicion.validaciones.all())
            estado_consolidado = service.consolidar_desde_validaciones(
                tipo_solicitud="RENDICION_CUENTAS",
                validaciones=validaciones_memoria,
                metodo_resolucion=MetodoResolucion.DECISORIO
            )

            #Clasificacion de contadores segun la respuesta del motor
            if estado_consolidado == 'APROBADO':
                aprobadas += 1
            elif estado_consolidado == 'RECHAZADO':
                rechazadas += 1
            elif estado_consolidado == 'PENDIENTE':
                pendientes += 1
            elif estado_consolidado in ['SIN_VALIDACIONES', 'SIN_REVISORES']:
                borradores += 1

        # for rendicion in rendiciones:
        #     validaciones = rendicion.validaciones.all()
        #     if not validaciones.exists():
        #         borradores += 1
        #         continue
        #     estados = set(validaciones.values_list('estado', flat=True))
        #     if 'RECHAZADO' in estados:
        #         rechazadas += 1
        #     elif estados == {'APROBADO'}:
        #         aprobadas += 1
        #     else:
        #         pendientes += 1

        return {
            'creadas': creadas,
            'aprobadas': aprobadas,
            'rechazadas': rechazadas,
            'pendientes': pendientes,
            'borradores': borradores,
        }
    
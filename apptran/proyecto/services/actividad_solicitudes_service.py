# spme/apptran/proyecto/services/actividad_solicitudes_service.py
# api/v2/services/actividad_solicitudes_service.py
from django.core.paginator import Paginator

from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudReembolso,
)

from spme_validaciones.services.consolidacion.service import (
    ConsolidacionValidacionService,
)
from spme_validaciones.services.consolidacion.modelos import (
    MetodoResolucion,
    EstadoConsolidado,
)

from ..repositories.actividad_solicitudes_repository import (
    ActividadSolicitudesRepository,
)

from collections import defaultdict


class ActividadSolicitudesService:
    """Servicio para actividades con solicitudes."""

    TIPOS_SOLICITUD = {
        'fondos': ('SOLICITUD_FONDOS', SolicitudFondos),
        'viajes': ('SOLICITUD_VIAJE', SolicitudViaje),
        'pagos_directos': ('SOLICITUD_PAGO_DIRECTO', SolicitudPagoDirecto),
        'reposiciones': ('SOLICITUD_REEMBOLSO', SolicitudReembolso),
    }

    def __init__(self):
        self.repository = ActividadSolicitudesRepository()
        self.consolidacion_service = ConsolidacionValidacionService()

    def obtener_actividades(
        self,
        usuario,
        filtros=None,
        page=1,
        page_size=20,
    ):
        """
        Obtiene lista paginada de actividades con tareas y badges.
        """
        queryset = self.repository.get_actividades_con_tareas(
            usuario=usuario,
            filtros=filtros,
        )

        paginator = Paginator(queryset, page_size)
        pagina = paginator.get_page(page)

        resultados = []

        for actividad in pagina:
            data = self._serializar_actividad(actividad)
            resultados.append(data)

        return {
            'results': resultados,
            'pagination': {
                'count': paginator.count,
                'page': pagina.number,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            },
        }

    def _serializar_actividad(self, actividad):
        """
        Convierte una actividad al formato de respuesta.
        """
        solicitudes_tareas = self._obtener_solicitudes_tareas_por_tipo(
            actividad.id
        )
        return {
            'id': actividad.id,
            'codigo': actividad.codigo or '',
            'nombre_corto': actividad.nombreCorto or '',
            'descripcion': actividad.descripcion or '',
            'estado': actividad.estado,
            'presupuesto': float(actividad.presupuesto or 0),
            'procedencia_fondos': actividad.procedencia_fondos,
            'fecha_programada': (
                actividad.fecha_programada.isoformat()
                if actividad.fecha_programada else None
            ),
            'duracion': (
                (actividad.fecha_cierre - actividad.fecha_inicio).days
                if actividad.fecha_inicio and actividad.fecha_cierre
                else None
            ),
            'fecha_inicio': (
                actividad.fecha_inicio.isoformat()
                if actividad.fecha_inicio else None
            ),
            'fecha_cierre': (
                actividad.fecha_cierre.isoformat()
                if actividad.fecha_cierre else None
            ),
            'responsable': (
                {
                    'id': actividad.responsable.id,
                    'nombre': actividad.responsable.get_full_name(),
                }
                if actividad.responsable else None
            ),
            'proyecto': (
                {
                    'id': actividad.proyecto.id,
                    'nombre': actividad.proyecto.titulo,
                }
                if actividad.proyecto else None
            ),
            'badges': self._obtener_badges_actividad(actividad.id),
            'tareas': [
                self._serializar_tarea(
                    # actividad.id,
                    tarea,
                    solicitudes_tareas,
                )
                for tarea in actividad.tareas.all()
            ],
        }

    def _serializar_tarea(self, tarea, solicitudes_tareas,):
        return {
            'id': tarea.id,
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.estado,
            'codigo': tarea.codigo or '',
            'badges': self._obtener_badges_tarea_desde_solicitudes(
                tarea.id,
                solicitudes_tareas,
            ),
        }

    # def _serializar_tarea(self, actividad_id, tarea):
    #     """Convierte una tarea al formato de respuesta."""
    #     return {
    #         'id': tarea.id,
    #         'titulo': tarea.titulo or '',
    #         'descripcion': tarea.descripcion or '',
    #         'estado': tarea.estado,
    #         'codigo': tarea.codigo or '',
    #         'badges': self._obtener_badges_tarea(
    #             actividad_id,
    #             tarea.id,
    #         ),
    #     }

    def _obtener_badges_tarea_desde_solicitudes(
        self,
        tarea_id,
        solicitudes_tareas,
    ):
        badges = {}

        for nombre_badge, (tipo, modelo) in self.TIPOS_SOLICITUD.items():
            solicitudes = solicitudes_tareas[nombre_badge].get(
                tarea_id,
                [],
            )

            badges[nombre_badge] = self._consolidar_solicitudes(
                solicitudes,
                tipo,
            )

        return badges

    def _obtener_badges_actividad(self, actividad_id):
        """
        Obtiene los badges de las solicitudes asociadas
        directamente a una actividad.
        """
        badges = {}

        for nombre_badge, (tipo, modelo) in self.TIPOS_SOLICITUD.items():
            solicitudes = self.repository.obtener_solicitudes_actividad(
                modelo,
                actividad_id,
            )

            badges[nombre_badge] = self._consolidar_solicitudes(
                solicitudes,
                tipo,
            )

        return badges

    # def _obtener_badges_tarea(self, actividad_id, tarea_id):
    #     """
    #     Obtiene los badges de las solicitudes asociadas
    #     a una tarea.
    #     """
    #     badges = {}

    #     for nombre_badge, (tipo, modelo) in self.TIPOS_SOLICITUD.items():
    #         solicitudes = self.repository.obtener_solicitudes_tarea(
    #             modelo,
    #             actividad_id,
    #             tarea_id,
    #         )

    #         badges[nombre_badge] = self._consolidar_solicitudes(
    #             solicitudes,
    #             tipo,
    #         )

    #     return badges

    def _consolidar_solicitudes(self, solicitudes, tipo):
        """
        Consolida las solicitudes y transforma los estados
        consolidados en contadores de badges.
        """
        resultado = {
            'creadas': 0,
            'aprobadas': 0,
            'rechazadas': 0,
            'pendientes': 0,
            'borradores': 0,
        }

        for solicitud in solicitudes:
            resultado['creadas'] += 1

            estado = self.consolidacion_service.consolidar_desde_validaciones(
                tipo,
                solicitud.validaciones.all(),
                MetodoResolucion.DECISORIO,
            )

            if estado == EstadoConsolidado.APROBADO:
                resultado['aprobadas'] += 1

            elif estado == EstadoConsolidado.RECHAZADO:
                resultado['rechazadas'] += 1

            elif estado == EstadoConsolidado.PENDIENTE:
                resultado['pendientes'] += 1

            elif estado == EstadoConsolidado.SIN_VALIDACIONES:
                resultado['borradores'] += 1

        return resultado

    def _obtener_solicitudes_tareas_por_tipo(self, actividad_id):
        resultado = {}

        for nombre_badge, (tipo, modelo) in self.TIPOS_SOLICITUD.items():
            solicitudes = self.repository.obtener_solicitudes_tareas_actividad(
                modelo,
                actividad_id,
            )

            agrupadas = defaultdict(list)

            for solicitud in solicitudes:
                agrupadas[solicitud.tarea_id].append(solicitud)

            resultado[nombre_badge] = agrupadas

        return resultado


















# from django.core.paginator import Paginator
# from ..repositories.actividad_solicitudes_repository import ActividadSolicitudesRepository
# #Imports del servicio de consolidacion
# from spme_validaciones.services.consolidacion.service import (
#     ConsolidacionValidacionService,
# )
# from spme_validaciones.services.consolidacion.modelos import (
#     MetodoResolucion,
#     EstadoConsolidado,
# )

# class ActividadSolicitudesService:
#     """Servicio para actividades con solicitudes."""

#     def __init__(self):
#         self.repository = ActividadSolicitudesRepository()
#         self.consolidacion_service = ConsolidacionValidacionService()

#     def obtener_actividades(self, usuario, filtros=None, page=1, page_size=20):
#         """
#         Obtiene lista paginada de actividades con tareas y badges.
#         """
#         queryset = self.repository.get_actividades_con_tareas(
#             usuario=usuario, filtros=filtros
#         )

#         paginator = Paginator(queryset, page_size)
#         pagina = paginator.get_page(page)

#         resultados = []
#         for actividad in pagina:
#             data = self._serializar_actividad(actividad)
#             resultados.append(data)

#         return {
#             'results': resultados,
#             'pagination': {
#                 'count': paginator.count,
#                 'page': pagina.number,
#                 'page_size': page_size,
#                 'total_pages': paginator.num_pages,
#             },
#         }

#     def _serializar_actividad(self, actividad):
#         """Convierte una actividad al formato de respuesta."""
#         return {
#             'id': actividad.id,
#             'codigo': actividad.codigo or '',
#             'nombre_corto': actividad.nombreCorto or '',
#             'descripcion': actividad.descripcion or '',
#             'estado': actividad.estado,
#             'presupuesto': float(actividad.presupuesto or 0),
#             'procedencia_fondos': actividad.procedencia_fondos,
#             'fecha_programada': (
#                 actividad.fecha_programada.isoformat()
#                 if actividad.fecha_programada else None
#             ),
#             'duracion': (
#                 (actividad.fecha_cierre - actividad.fecha_inicio).days
#                 if actividad.fecha_inicio and actividad.fecha_cierre else None
#             ),
#             'fecha_inicio': (
#                 actividad.fecha_inicio.isoformat()
#                 if actividad.fecha_inicio else None
#             ),
#             'fecha_cierre': (
#                 actividad.fecha_cierre.isoformat()
#                 if actividad.fecha_cierre else None
#             ),
#             'responsable': (
#                 {
#                     'id': actividad.responsable.id,
#                     'nombre': actividad.responsable.get_full_name(),
#                 }
#                 if actividad.responsable else None
#             ),
#             'proyecto': (
#                 {
#                     'id': actividad.proyecto.id,
#                     'nombre': actividad.proyecto.titulo,
#                 }
#                 if actividad.proyecto else None
#             ),
#             'badges': self.repository.get_badges_actividad(actividad.id),
#             'tareas': [
#                 self._serializar_tarea(tarea)
#                 for tarea in actividad.tareas.all()
#             ],
#         }

#     def _serializar_tarea(self, tarea):
#         """Convierte una tarea al formato de respuesta."""
#         return {
#             'id': tarea.id,
#             'titulo': tarea.titulo or '',
#             'descripcion': tarea.descripcion or '',
#             'estado': tarea.estado,
#             'codigo': tarea.codigo or '',
#             'badges': self.repository.get_badges_tarea(tarea.id),
#         }
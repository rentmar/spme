#spme/spme_presupuesto/repositories/ejecucion_repository.py
"""
Repositorio de ejecución presupuestaria.

Encapsula las consultas de solicitudes aprobadas para calcular
el presupuesto ejecutado a nivel de actividad y tarea.
"""

from django.db.models import Q, Sum

#Modelos
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso,
    SolicitudViaje,
    SolicitudPagoDirecto,
)

#Servicio de aprobacion
from spme_presupuesto.services.validacion_solicitud_service import (
    es_aprobada_solicitud_fondos,
    es_aprobada_solicitud_reembolso,
    es_aprobada_solicitud_viaje,
    es_aprobada_solicitud_pago_directo,
)



class EjecucionRepository:
    """
    Consultas de ejecución presupuestaria
    """

    # Lista de modelos de solicitud con sus funciones de validación
    MODELOS_SOLICITUD = [
        (SolicitudFondos, es_aprobada_solicitud_fondos, 'Solicitud de Fondos'),
        (SolicitudReembolso, es_aprobada_solicitud_reembolso, 'Solicitud de Reembolso'),
        (SolicitudViaje, es_aprobada_solicitud_viaje, 'Solicitud de Viaje'),
        (SolicitudPagoDirecto, es_aprobada_solicitud_pago_directo, 'Pago Directo'),
    ]

    @classmethod
    def obtener_solicitudes_aprobadas_actividad(cls, actividad_id):
        """
        Obtiene todas las solicitudes aprobadas de una actividad.
        
        Incluye:
        - Solicitudes directas de la actividad (tarea IS NULL)
        - Solicitudes de las tareas de la actividad (tarea IS NOT NULL)
        
        Returns:
            list de dict con los datos de cada solicitud aprobada
        """
        resultado = []

        for modelo, func_aprobada, nombre_tipo in cls.MODELOS_SOLICITUD:
            solicitudes = modelo.objects.filter(actividad_id=actividad_id)
            for sol in solicitudes:
                if func_aprobada(sol):
                    resultado.append({
                        'tipo': nombre_tipo,
                        'numero': sol.numeroFormulario or '',
                        'monto': float(sol.montoSolicitado or 0),
                        'fecha': sol.fechaSolicitud,
                        'tarea_id': sol.tarea_id,
                        'es_directa': sol.tarea_id is None,
                    })
        return sorted(resultado, key=lambda x: x['fecha'] or '')
    
    @classmethod
    def obtener_solicitudes_aprobadas_tarea(cls, tarea_id):
        """
        Obtiene todas las solicitudes aprobadas de una tarea.
        
        Returns:
            list de dict con los datos de cada solicitud aprobada
        """

        resultado = []

        for modelo, func_aprobada, nombre_tipo in cls.MODELOS_SOLICITUD:
            solicitudes = modelo.objects.filter(tarea_id=tarea_id)
            for sol in solicitudes:
                if func_aprobada(sol):
                    resultado.append({
                        'tipo': nombre_tipo,
                        'numero': sol.numeroFormulario or '',
                        'monto': float(sol.montoSolicitado or 0),
                        'fecha': sol.fechaSolicitud,
                    })
        
        return sorted(resultado, key=lambda x: x['fecha'] or '')
    
    @classmethod
    def total_ejecutado_actividad(cls, actividad_id):
        """
        Calcula el total ejecutado de una actividad.
        
        Suma las solicitudes directas de la actividad (sin tarea)
        más las solicitudes de todas sus tareas.
        """

        total = 0

        for modelo, func_aprobada, _ in cls.MODELOS_SOLICITUD:
            # Solicitudes directas de la actividad
            for sol in modelo.objects.filter(actividad_id=actividad_id, tarea__isnull=True):
                if func_aprobada(sol):
                    total += float(sol.montoSolicitado or 0)

            # Solicitudes de las tareas de la actividad
            for sol in modelo.objects.filter(actividad_id=actividad_id, tarea__isnull=False):
                if func_aprobada(sol):
                    total += float(sol.montoSolicitado or 0)
        
        return total
    
    @classmethod
    def total_ejecutado_tarea(cls, tarea_id):
        """
        Calcula el total ejecutado de una tarea.
        """
        total = 0

        for modelo, func_aprobada, _ in cls.MODELOS_SOLICITUD:
            for sol in modelo.objects.filter(tarea_id=tarea_id):
                if func_aprobada(sol):
                    total += float(sol.montoSolicitado or 0)

        return total
    
    @classmethod
    def total_ejecutado_proyecto(cls, proyecto_id):
        """
        Calcula el total ejecutado de un proyecto.
        Suma el ejecutado de todas sus actividades activas.
        """

        from spme_actividades.models import Actividad

        total = 0
        actividades = Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False
        )

        for act in actividades:
            total += cls.total_ejecutado_actividad(act.id)

        return total



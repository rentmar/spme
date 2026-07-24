from typing import Dict, Any
from spme_validaciones.models import (
    ValidacionSolicitudFondos,
    ValidacionSolicitudViaje,
    ValidacionSolicitudPagoDirecto,
    ValidacionSolicitudReembolso,
)

from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudReembolso,
)

import logging


logger = logging.getLogger(__name__)


class EstadoConsolidadoSolicitudesService:
    """
    Servicio para determinar el estado consolidado de una solicitud
    """
    #Estado de la solicitud
    ESTADO_SIN_REVISORES = 'SIN_REVISORES'
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_APROBADO = 'APROBADO'
    ESTADO_RECHAZADO = 'RECHAZADO'

    #Mapeo de los modelos
    MAPEO_VALIDACIONES = {
        SolicitudFondos: ValidacionSolicitudFondos,
        SolicitudViaje: ValidacionSolicitudViaje,
        SolicitudPagoDirecto: ValidacionSolicitudPagoDirecto,
        SolicitudReembolso: ValidacionSolicitudReembolso,
    }

    def obtener_estado_consolidado(self, solicitud) -> Dict[str, Any]:
        """
        Determina el estado consolidado de una solicitud.
        
        Args:
            solicitud: Instancia de SolicitudFondos, SolicitudViaje, etc.
            
        Returns:
            Dict con el estado consolidado
        """
        #Obtener clase de validacion del mapeo
        validacion_class = self.MAPEO_VALIDACIONES.get(type(solicitud))

        if not validacion_class:
            raise ValueError(f"Tipo de solicitud no soportado: {type(solicitud).__name__}")

        #Obtener validaciones
        validaciones = validacion_class.objects.filter(solicitud=solicitud)

        #Estado sin revisores
        if not validaciones.exists():
            return{
                'estado': self.ESTADO_SIN_REVISORES,
                'estado_display': 'Sin Revisores'
            }

        # Si al menos una está RECHAZADA → RECHAZADO
        if validaciones.filter(estado='RECHAZADO').exists():
            return {
                'estado': self.ESTADO_RECHAZADO,
                'estado_display': 'Rechazado'
            }

        # Si al menos una está PENDIENTE → PENDIENTE
        if validaciones.filter(estado='PENDIENTE').exists():
            return {
                'estado': self.ESTADO_PENDIENTE,
                'estado_display': 'Pendiente'
            }

        # Todas APROBADO → APROBADO
        return {
            'estado': self.ESTADO_APROBADO,
            'estado_display': 'Aprobado'
        }



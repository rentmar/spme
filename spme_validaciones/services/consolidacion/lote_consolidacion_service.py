# spme/spme_validaciones/services/consolidacion/lote_consolidacion_service.py
from typing import List, Dict, Any
from .service import ConsolidacionValidacionService
from .modelos import MetodoResolucion
import logging

logger = logging.getLogger(__name__)


class LoteConsolidacionService:
    """
    Servicio centralizado para procesar lotes de solicitudes y rendiciones 
    aprovechando validaciones ya cargadas en memoria.
    """
    def __init__(self):
        self.consolidacionService = ConsolidacionValidacionService()

    def procesarLoteEnMemoria(
        self,
        tipo_solicitud: str,
        solicitudes: List[Any],
        metodo_resolucion: str = MetodoResolucion.DECISORIO,    
    )->dict[int, str]:
        """
        Toma una lista de objetos de solicitud (que ya tienen sus validaciones en prefetch)
        y devuelve un diccionario mapeando id_solicitud -> estado consolidado del motor.
        Args:
            tipo_solicitud: Ej. "SOLICITUD_FONDOS", "SOLICITUD_VIAJE", etc.
            solicitudes: QuerySet o lista de instancias de modelos de solicitudes.
            metodo_resolucion: Por defecto DECISORIO.
        
        Returns:
            Dict[int, str]: Ejemplo {101: "APROBADO", 102: "PENDIENTE", 103: "RECHAZADO"}
        """
        #Defino el objeto de resultados
        resultados = {}

        for solicitud in solicitudes:
            try:
                #Extraer las validaciones cargadas en memoria por el prefetch_related
                validaciones = solicitud.validaciones.all() if hasattr(solicitud, 'validaciones') else []

                #Ejecutar el metodo central para calculo en memoria
                estado_motor = self.consolidacionService.consolidar_desde_validaciones(
                    tipo_solicitud=tipo_solicitud,
                    validaciones=validaciones,
                    metodo_resolucion=metodo_resolucion,
                )

                resultados[solicitud.id] = estado_motor

            except Exception as e:
                logger.error(
                    f"Error al consolidar lote para {tipo_solicitud} [ID: {solicitud.id}]: {str(e)}",
                    exc_info=True
                )
                resultados[solicitud.id] = "PENDIENTE"

        return resultados



# spme_validaciones/services/peticiones/handlers/edicion_total_handler.py

"""
Handler para el tipo EDICION_TOTAL.

Efecto:
    1. Genera un snapshot del documento actual en DocumentoVersion.
    2. No modifica el documento. La habilitación de edición es responsabilidad
       del frontend (recalcula localmente) y del endpoint de guardado (que
       verifica la petición ejecutada no consumida).
"""
from spme_validaciones.constants_peticiones import TIPO_EDICION_TOTAL
from spme_validaciones.services.peticiones.handlers.registry import registrar_handler
from spme_validaciones.services.peticiones.documento_version_service import (
    DocumentoVersionService,
)


@registrar_handler(TIPO_EDICION_TOTAL)
def ejecutar_edicion_total(peticion, documento):
    """
    Al ejecutarse, deja registrada la versión vigente del documento.
    El documento no se modifica.

    Args:
        peticion: instancia de PeticionModificacion ya validada.
        documento: instancia del modelo objetivo resuelta.
    """
    # service = DocumentoVersionService()
    # service.crear_snapshot(
    #     documento=documento,
    #     peticion=peticion,
    #     aprobado_por=peticion.solicitante,
    # )
    return None
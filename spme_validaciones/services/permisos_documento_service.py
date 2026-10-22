# spme/spme_validaciones/services/permisos_documento_service.py
from dataclasses import dataclass
from typing import Optional, Sequence

from spme_autenticacion.models import Usuario
from spme_validaciones.constants import (
    MOTIVO_NO_ES_REDACTOR,
    MOTIVO_APROBADO_SIN_EDICION,
    MOTIVO_PENDIENTE_CON_VOTOS,
    MOTIVO_PETICION_ABIERTA,
    ESTADO_SIN_REVISORES,
    ESTADO_PENDIENTE,
    ESTADO_RECHAZADO,
    ESTADO_APROBADO,
)
from spme_validaciones.services.consolidacion.modelos import EstadoConsolidado

@dataclass(frozen=True)
class PermisosDocumento:
    puede_editar: bool
    es_redactor: bool
    puede_solicitar_modificacion: bool
    motivo_bloqueo: Optional[str]
    estado_documento: str

# ===================================================================
# HELPERS PUROS (testeables sin DB)
# ===================================================================
def _mapear_estado(estado_consolidado: str) -> str:
    """
    Traduce el EstadoConsolidado del motor (única fuente de verdad) 
    a los estados del contrato del endpoint.
    """
    mapping = {
        EstadoConsolidado.SIN_VALIDACIONES: ESTADO_SIN_REVISORES,
        EstadoConsolidado.RECHAZADO: ESTADO_RECHAZADO,
        EstadoConsolidado.APROBADO: ESTADO_APROBADO,
        EstadoConsolidado.PENDIENTE: ESTADO_PENDIENTE,
    }
    return mapping.get(estado_consolidado, ESTADO_PENDIENTE)

def _tiene_peticion_abierta(documento) -> bool:
    """
    Hook reservado para el sistema de peticiones de modificación.

    HOY: devuelve False.

    MAÑANA (cuando exista PeticionModificacion), reemplazar por la
    consulta real. Único lugar a tocar.
    """
    # TODO: implementar cuando PeticionModificacion esté listo
    # return False
    from spme_validaciones.services.peticiones.peticion_service import PeticionService
    return PeticionService().tiene_peticion_abierta(documento)


def _puede_solicitar(documento, usuario: Usuario) -> bool:
    """
    Hook reservado para el sistema de peticiones de modificación.
    HOY: devuelve False.
    """
    # TODO: implementar cuando PeticionModificacion esté listo
    # return False
    from spme_validaciones.services.peticiones.peticion_service import PeticionService
    return PeticionService().puede_solicitar_modificacion(documento, usuario)


# ===================================================================
# CÁLCULO PRINCIPAL
# ===================================================================
def calcular_permisos(
        documento, 
        usuario: Usuario,
        estado_consolidado: str, 
        validaciones: Sequence = ()
    ) -> PermisosDocumento:
    """
    Calcula los permisos de un documento para un usuario dado.

    Args:
        documento: instancia del documento (SolicitudFondos, etc.)
        usuario: usuario autenticado (viene de request.user)
        resumen: dict con conteos, viene del repository

    Returns:
        PermisosDocumento (inmutable)
    """

    estado = _mapear_estado(estado_consolidado)

    # El redactor es quien creó el documento.
    es_redactor = documento.usuario_id == usuario.id

    # --- No es redactor: nunca edita ---
    if not es_redactor:
        return PermisosDocumento(
            puede_editar=False,
            es_redactor=False,
            puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
            motivo_bloqueo=MOTIVO_NO_ES_REDACTOR,
            estado_documento=estado,
        )

    # --- Petición abierta (hook reservado) ---
    if _tiene_peticion_abierta(documento):
        return PermisosDocumento(
            puede_editar=False,
            es_redactor=True,
            puede_solicitar_modificacion=False,
            motivo_bloqueo=MOTIVO_PETICION_ABIERTA,
            estado_documento=estado,
        )

    # --- Sin revisores: libre ---
    if estado_consolidado == EstadoConsolidado.SIN_VALIDACIONES:
        return PermisosDocumento(
            puede_editar=True,
            es_redactor=True,
            puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
            motivo_bloqueo=None,
            estado_documento=ESTADO_SIN_REVISORES,
        )

    # --- Aprobado: consolidado ---
    if estado_consolidado == EstadoConsolidado.APROBADO:
        return PermisosDocumento(
            puede_editar=False,
            es_redactor=True,
            puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
            motivo_bloqueo=MOTIVO_APROBADO_SIN_EDICION,
            estado_documento=ESTADO_APROBADO,
        )
    
    # --- Rechazado: puede corregir ---
    if estado_consolidado == EstadoConsolidado.RECHAZADO:
        return PermisosDocumento(
            puede_editar=True,
            es_redactor=True,
            puede_solicitar_modificacion=False,
            motivo_bloqueo=None,
            estado_documento=ESTADO_RECHAZADO,
        )

    # --- Pendiente con al menos un voto: bloqueado ---
    votos_emitidos = any(v.estado in ('APROBADO', 'RECHAZADO') for v in validaciones)
    if votos_emitidos:
        return PermisosDocumento(
            puede_editar=False,
            es_redactor=True,
            puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
            motivo_bloqueo=MOTIVO_PENDIENTE_CON_VOTOS,
            estado_documento=ESTADO_PENDIENTE,
        )

    # --- Pendiente sin votos: libre ---
    return PermisosDocumento(
        puede_editar=True,
        es_redactor=True,
        puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
        motivo_bloqueo=None,
        estado_documento=ESTADO_PENDIENTE,
    )
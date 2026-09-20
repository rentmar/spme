# spme/spme_validaciones/services/permisos_documento_service.py
from dataclasses import dataclass
from typing import Optional

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
def _mapear_estado(resumen: dict) -> str:
    """
    Traduce el resumen del repository a los 4 estados del contrato.
    Resumen esperado:
        {
            'total': int,
            'pendientes': int,
            'aprobados': int,
            'rechazados': int,
            'completado': bool,
            'aprobado_totalmente': bool,
            'rechazado': bool,
        }
    """
    total = resumen.get('total', 0)
    if total == 0:
        return ESTADO_SIN_REVISORES
    if resumen.get('rechazado'):
        return ESTADO_RECHAZADO
    if resumen.get('aprobado_totalmente'):
        return ESTADO_APROBADO
    return ESTADO_PENDIENTE

def _tiene_peticion_abierta(documento) -> bool:
    """
    Hook reservado para el sistema de peticiones de modificación.

    HOY: devuelve False.

    MAÑANA (cuando exista PeticionModificacion), reemplazar por la
    consulta real. Único lugar a tocar.
    """
    # TODO: implementar cuando PeticionModificacion esté listo
    return False


def _puede_solicitar(documento, usuario: Usuario) -> bool:
    """
    Hook reservado para el sistema de peticiones de modificación.
    HOY: devuelve False.
    """
    # TODO: implementar cuando PeticionModificacion esté listo
    return False


# ===================================================================
# CÁLCULO PRINCIPAL
# ===================================================================
def calcular_permisos(documento, usuario: Usuario, resumen: dict) -> PermisosDocumento:
    """
    Calcula los permisos de un documento para un usuario dado.

    Args:
        documento: instancia del documento (SolicitudFondos, etc.)
        usuario: usuario autenticado (viene de request.user)
        resumen: dict con conteos, viene del repository

    Returns:
        PermisosDocumento (inmutable)
    """

    estado = _mapear_estado(resumen)

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
    if resumen['total'] == 0:
        return PermisosDocumento(
            puede_editar=True,
            es_redactor=True,
            puede_solicitar_modificacion=False,
            motivo_bloqueo=None,
            estado_documento=ESTADO_SIN_REVISORES,
        )

    # --- Aprobado: consolidado ---
    if resumen['aprobado_totalmente']:
        return PermisosDocumento(
            puede_editar=False,
            es_redactor=True,
            puede_solicitar_modificacion=_puede_solicitar(documento, usuario),
            motivo_bloqueo=MOTIVO_APROBADO_SIN_EDICION,
            estado_documento=ESTADO_APROBADO,
        )

    # --- Rechazado: puede corregir ---
    if resumen['rechazado']:
        return PermisosDocumento(
            puede_editar=True,
            es_redactor=True,
            puede_solicitar_modificacion=False,
            motivo_bloqueo=None,
            estado_documento=ESTADO_RECHAZADO,
        )

    # --- Pendiente con al menos un voto: bloqueado ---
    votos_emitidos = resumen['aprobados'] + resumen['rechazados']
    if votos_emitidos > 0:
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
        puede_solicitar_modificacion=False,
        motivo_bloqueo=None,
        estado_documento=ESTADO_PENDIENTE,
    )
# spme/spme_validaciones/constants.py
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudReembolso,
    RendicionCuentas,
)
from .repositories.validacion_solicitud_fondos_repository import (
    ValidacionSolicitudFondosRepository,
)
from .repositories.validacion_solicitud_viaje_repository import (
    ValidacionSolicitudViajeRepository,
)
from .repositories.validacion_solicitud_pago_directo_repository import (
    ValidacionSolicitudPagoDirectoRepository,
)
from .repositories.validacion_solicitud_reembolso_repository import (
    ValidacionSolicitudReembolsoRepository,
)
from .repositories.validacion_rendicion_cuentas_repository import (
    ValidacionRendicionCuentasRepository,
)


# ===================================================================
# MAPEO TIPO → (MODELO, REPOSITORY, CAMPO_FK)
# ===================================================================
TIPOS_DOCUMENTO = {
    'solicitud-fondos': {
        'modelo': SolicitudFondos,
        'repository': ValidacionSolicitudFondosRepository,
        'campo_fk': 'solicitud',
    },
    'solicitud-viaje': {
        'modelo': SolicitudViaje,
        'repository': ValidacionSolicitudViajeRepository,
        'campo_fk': 'solicitud',
    },
    'solicitud-pago-directo': {
        'modelo': SolicitudPagoDirecto,
        'repository': ValidacionSolicitudPagoDirectoRepository,
        'campo_fk': 'solicitud',
    },
    'solicitud-reembolso': {
        'modelo': SolicitudReembolso,
        'repository': ValidacionSolicitudReembolsoRepository,
        'campo_fk': 'solicitud',
    },
    'rendicion-cuentas': {
        'modelo': RendicionCuentas,
        'repository': ValidacionRendicionCuentasRepository,
        'campo_fk': 'rendicion',
    },
}

# ===================================================================
# CÓDIGOS DE MOTIVO DE BLOQUEO (contrato con frontend)
# ===================================================================
MOTIVO_NO_ES_REDACTOR = 'NO_ES_REDACTOR'
MOTIVO_SIN_REVISORES = 'SIN_REVISORES'
MOTIVO_APROBADO_SIN_EDICION = 'APROBADO_SIN_EDICION'
MOTIVO_PENDIENTE_CON_VOTOS = 'PENDIENTE_CON_VOTOS'
MOTIVO_PETICION_ABIERTA = 'PETICION_MODIFICACION_ABIERTA'

# ===================================================================
# ESTADOS DEL DOCUMENTO (contrato con frontend)
# ===================================================================
ESTADO_SIN_REVISORES = 'SIN_REVISORES'
ESTADO_PENDIENTE = 'PENDIENTE'
ESTADO_RECHAZADO = 'RECHAZADO'
ESTADO_APROBADO = 'APROBADO'

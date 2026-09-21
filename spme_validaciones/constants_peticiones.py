# spme_validaciones/constants_peticiones.py

# ===================================================================
# ESTADOS DE PETICIÓN
# ===================================================================
ESTADO_INICIADA = 'INICIADA'
ESTADO_RESUELTA_EJECUTADA = 'RESUELTA_EJECUTADA'
ESTADO_RESUELTA_ANULADA = 'RESUELTA_ANULADA'

ESTADOS_PETICION = [
    (ESTADO_INICIADA, 'Iniciada'),
    (ESTADO_RESUELTA_EJECUTADA, 'Resuelta (ejecutada)'),
    (ESTADO_RESUELTA_ANULADA, 'Resuelta (anulada)'),
]

# ===================================================================
# CÓDIGOS DE TIPO DE PETICIÓN
# ===================================================================
TIPO_EDICION_TOTAL = 'EDICION_TOTAL'
TIPO_CAMBIO_REVISOR_SECUNDARIO = 'CAMBIO_REVISOR_SECUNDARIO'
TIPO_REASIGNACION_ESTRUCTURA = 'REASIGNACION_ESTRUCTURA'
TIPO_CAMBIO_REDACTOR = 'CAMBIO_REDACTOR'

# ===================================================================
# CARGO ADMIN
# ===================================================================
CARGO_ADMIN = 'admin'
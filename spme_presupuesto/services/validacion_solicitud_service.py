"""
Servicio de validación de solicitudes para ejecución presupuestaria.

Cada tipo de solicitud tiene su propia función es_aprobada().
Esto permite que los criterios de aprobación puedan variar
independientemente en futuras versiones sin afectar a los demás.

Regla actual (v2.0):
    Una solicitud está aprobada cuando:
    - validacionResponsable == True
    - validacionCoordinador == True

Para agregar un nuevo tipo de solicitud o modificar criterios:
    1. Agregar/modificar la función es_aprobada_<tipo>()
    2. Actualizar TIPOS_SOLICITUD
    3. Agregar la señal correspondiente en signals.py
"""


def es_aprobada_solicitud_fondos(solicitud):
    """
    Determina si una Solicitud de Fondos está aprobada.
    
    Criterio (v2.0):
        - validacionResponsable == True
        - validacionCoordinador == True
    
    Args:
        solicitud: Instancia de SolicitudFondos
        
    Returns:
        bool: True si la solicitud está aprobada
    """
    return (
        solicitud.validacionResponsable == True and
        solicitud.validacionCoordinador == True
    )


def es_aprobada_solicitud_reembolso(solicitud):
    """
    Determina si una Solicitud de Reembolso está aprobada.
    
    Criterio (v2.0):
        - validacionResponsable == True
        - validacionCoordinador == True
    
    Args:
        solicitud: Instancia de SolicitudReembolso
        
    Returns:
        bool: True si la solicitud está aprobada
    """
    return (
        solicitud.validacionResponsable == True and
        solicitud.validacionCoordinador == True
    )


def es_aprobada_solicitud_viaje(solicitud):
    """
    Determina si una Solicitud de Viaje está aprobada.
    
    Criterio (v2.0):
        - validacionResponsable == True
        - validacionCoordinador == True
    
    Args:
        solicitud: Instancia de SolicitudViaje
        
    Returns:
        bool: True si la solicitud está aprobada
    """
    return (
        solicitud.validacionResponsable == True and
        solicitud.validacionCoordinador == True
    )


def es_aprobada_solicitud_pago_directo(solicitud):
    """
    Determina si una Solicitud de Pago Directo está aprobada.
    
    Criterio (v2.0):
        - validacionResponsable == True
        - validacionCoordinador == True
    
    Args:
        solicitud: Instancia de SolicitudPagoDirecto
        
    Returns:
        bool: True si la solicitud está aprobada
    """
    return (
        solicitud.validacionResponsable == True and
        solicitud.validacionCoordinador == True
    )


# ─── Mapeo de tipos de solicitud a funciones de validación ───

TIPOS_SOLICITUD = {
    'SolicitudFondos': es_aprobada_solicitud_fondos,
    'SolicitudReembolso': es_aprobada_solicitud_reembolso,
    'SolicitudViaje': es_aprobada_solicitud_viaje,
    'SolicitudPagoDirecto': es_aprobada_solicitud_pago_directo,
}


def es_solicitud_aprobada(solicitud):
    """
    Función genérica que determina si cualquier tipo de solicitud está aprobada.
    
    Args:
        solicitud: Instancia de cualquier tipo de solicitud
        
    Returns:
        bool: True si la solicitud está aprobada
        
    Raises:
        ValueError: Si el tipo de solicitud no está registrado en TIPOS_SOLICITUD
    """
    tipo = type(solicitud).__name__
    
    if tipo in TIPOS_SOLICITUD:
        return TIPOS_SOLICITUD[tipo](solicitud)
    
    raise ValueError(f"Tipo de solicitud no registrado: {tipo}")

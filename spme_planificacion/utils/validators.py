#Validadores
from .acciones import ACCIONES_CATALOGO, ACCIONES_ACTIVIDAD, TIPOS_ELEMENTO

def normalizar_accion(accion):
    if not accion:
        return 'EDITAR'
    return accion.upper().strip()


def normalizar_tipo(tipo):
    if not tipo:
        return 'actividad'
    return tipo.lower().strip()


def validar_accion(accion, tipo_elemento):
    if accion not in ACCIONES_CATALOGO:
        raise ValueError(
            f"Acción '{accion}' no reconocida. "
            f"Disponibles: {list(ACCIONES_CATALOGO.keys())}"
        )
    if tipo_elemento == 'actividad' and accion not in ACCIONES_ACTIVIDAD:
        raise ValueError(
            f"Acción '{accion}' no permitida para actividades. "
            f"Permitidas: {ACCIONES_ACTIVIDAD}"
        )
    return True


def validar_tipo(tipo):
    if tipo not in TIPOS_ELEMENTO:
        raise ValueError(
            f"Tipo '{tipo}' no reconocido. "
            f"Disponibles: {TIPOS_ELEMENTO}"
        )
    return True
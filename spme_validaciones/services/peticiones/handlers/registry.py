# spme_validaciones/services/peticiones/handlers/registry.py

"""
Registro de handlers por código de tipo de petición.

Un handler es una función con firma:
    handler(peticion, documento) -> None

- Recibe la petición (PeticionModificacion) y el documento resuelto.
- Aplica el efecto del tipo sobre el documento.
- No se encarga de transiciones de estado; el servicio lo hace.
- No captura excepciones; el servicio las propaga.
"""
from typing import Callable, Dict

_HANDLERS: Dict[str, Callable] = {}


def registrar_handler(codigo: str):
    """Decorador para registrar un handler bajo un código de tipo."""
    def decorator(func: Callable):
        if codigo in _HANDLERS:
            raise ValueError(f"Handler duplicado para el código '{codigo}'")
        _HANDLERS[codigo] = func
        return func
    return decorator


def obtener_handler(codigo: str) -> Callable:
    """Devuelve el handler para el código, o None si no existe."""
    return _HANDLERS.get(codigo)


def listar_codigos_registrados():
    """Devuelve la lista de códigos con handler registrado."""
    return sorted(_HANDLERS.keys())
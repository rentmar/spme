# spme_validaciones/services/peticiones/handlers/__init__.py

from .registry import (  # noqa
    registrar_handler,
    obtener_handler,
    listar_codigos_registrados,
)

# Importar handlers para que se registren al cargar el paquete.
from . import edicion_total_handler  # noqa
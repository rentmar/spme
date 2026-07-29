"""
Catálogo de acciones del sistema de seguimiento.
Agregar nuevas acciones aquí NO requiere migraciones.
"""

ACCIONES_CATALOGO = {
    'AGREGAR': 'Agregar',
    'EDITAR': 'Editar',
    'ELIMINAR': 'Eliminar',
    'HABILITAR': 'Habilitar',
    'DESHABILITAR': 'Deshabilitar',
}

ACCIONES_ACTIVIDAD = ['AGREGAR', 'EDITAR', 'ELIMINAR', 'HABILITAR', 'DESHABILITAR']

TIPOS_ELEMENTO = ['actividad', 'tarea']


def get_accion_display(accion):
    """Devuelve el nombre legible de una acción."""
    return ACCIONES_CATALOGO.get(accion, accion)
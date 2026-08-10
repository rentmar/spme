"""Excepciones propias para la capa de servicios."""


class StorageError(Exception):
    """Error base de almacenamiento."""
    pass


class ArchivoCreationError(StorageError):
    """Error al crear registro Archivo en MySQL."""
    pass


class AdjuntoCreationError(StorageError):
    """Error al crear registro Adjunto en MySQL."""
    pass


class ArchivoIntegrityError(StorageError):
    """Error de integridad: key duplicada."""
    pass


class AdjuntoNotFoundError(StorageError):
    """El adjunto no existe."""
    pass


class ArchivoNotFoundError(StorageError):
    """El archivo no existe."""
    pass


class ArchivoStillReferencedError(StorageError):
    """El archivo aún tiene adjuntos asociados."""
    pass
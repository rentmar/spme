"""Excepciones propias para el repositorio Garage."""


class GarageError(Exception):
    """Error base de Garage."""
    pass


class GarageConnectionError(GarageError):
    """No se puede conectar a Garage."""
    pass


class GarageObjectNotFoundError(GarageError):
    """El objeto no existe en Garage."""
    pass


class GarageBucketNotFoundError(GarageError):
    """El bucket no existe en Garage."""
    pass


class GarageUploadError(GarageError):
    """Error al subir archivo a Garage."""
    pass


class GarageDownloadError(GarageError):
    """Error al descargar archivo desde Garage."""
    pass


class GarageDeleteError(GarageError):
    """Error al eliminar archivo de Garage."""
    pass
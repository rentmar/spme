#utils/exceptions.py
class ReporteError(Exception):
    """Excepción base para errores del sistema de reportes."""
    def __init__(self, mensaje: str, codigo: str = None):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(mensaje)


class ElementoNoEncontradoError(ReporteError):
    def __init__(self, tipo_elemento: str, elemento_id: int):
        super().__init__(
            mensaje=f"{tipo_elemento} con ID {elemento_id} no encontrado",
            codigo='ELEMENTO_NO_ENCONTRADO'
        )


class ProfundidadInvalidaError(ReporteError):
    def __init__(self, profundidad: str):
        super().__init__(
            mensaje=f"Profundidad '{profundidad}' no válida.",
            codigo='PROFUNDIDAD_INVALIDA'
        )


class TipoElementoNoSoportadoError(ReporteError):
    def __init__(self, tipo: str, soportados: list):
        super().__init__(
            mensaje=f"Tipo '{tipo}' no soportado. Válidos: {soportados}",
            codigo='TIPO_NO_SOPORTADO'
        )


class GeneracionWordError(ReporteError):
    def __init__(self, detalle: str):
        super().__init__(
            mensaje=f"Error al generar documento Word: {detalle}",
            codigo='ERROR_GENERACION_WORD'
        )
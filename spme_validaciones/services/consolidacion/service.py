# spme/spme_validaciones/services/consolidacion/service.py
from .configuracion import ConfiguracionConsolidacion
from .modelos import ContextoConsolidacion, VotoValidacion
from .motor import MotorConsolidacion
from spme_validaciones.repositories.consolidacion_validacion_repository import (
    ConsolidacionValidacionRepository,
)



class ConsolidacionValidacionService:

    def __init__(self):
        self.repository = ConsolidacionValidacionRepository()
        self.configuracion = ConfiguracionConsolidacion()
        self.motor = MotorConsolidacion()

    def consolidar(
        self,
        tipo_solicitud,
        solicitud_id,
        metodo_resolucion,
    ):
        # 1. Obtener las validaciones del documento
        validaciones = self.repository.obtener_validaciones(
            tipo_solicitud,
            solicitud_id,
        )

        return self.consolidar_desde_validaciones(
            tipo_solicitud,
            validaciones,
            metodo_resolucion,
        )

    def consolidar_desde_validaciones(
        self,
        tipo_solicitud,
        validaciones,
        metodo_resolucion,
    ):
        configuracion = self.configuracion.obtener(
            tipo_solicitud,
            metodo_resolucion,
        )

        votos = tuple(
            VotoValidacion(
                usuario_id=validacion.usuarioValidador_id,
                estado=validacion.estado,
            )
            for validacion in validaciones
        )

        contexto = ContextoConsolidacion(
            metodo_resolucion=metodo_resolucion,
            configuracion=configuracion,
            votos=votos,
        )

        return self.motor.consolidar(contexto)

# class ConsolidacionValidacionService:

#     def __init__(self):
#         self.repository = ConsolidacionValidacionRepository()
#         self.configuracion = ConfiguracionConsolidacion()
#         self.motor = MotorConsolidacion()

#     def consolidar(
#         self,
#         tipo_solicitud,
#         solicitud_id,
#         metodo_resolucion,
#     ):
#         # 1. Obtener las validaciones del documento
#         validaciones = self.repository.obtener_validaciones(
#             tipo_solicitud,
#             solicitud_id,
#         )

#         # 2. Obtener la configuración del método
#         configuracion = self.configuracion.obtener(
#             tipo_solicitud,
#             metodo_resolucion,
#         )

#         # 3. Normalizar las validaciones a votos
#         votos = tuple(
#             VotoValidacion(
#                 usuario_id=validacion.usuarioValidador_id,
#                 estado=validacion.estado,
#             )
#             for validacion in validaciones
#         )

#         # 4. Construir el contexto de consolidación
#         contexto = ContextoConsolidacion(
#             metodo_resolucion=metodo_resolucion,
#             configuracion=configuracion,
#             votos=votos,
#         )

#         # 5. Delegar el cálculo al motor
#         return self.motor.consolidar(contexto)
# spme/spme_validaciones/services/consolidacion/configuracion.py
from .modelos import ConfiguracionMetodo, MetodoResolucion

CONFIGURACIONES = {
    "SOLICITUD_FONDOS": {
        MetodoResolucion.DECISORIO: {
            "parametros": {
                "usuarioDecisorio": 46,
            },
        },
        MetodoResolucion.TODO_O_NADA:{
            "parametros": {},
        }
    },

    "SOLICITUD_VIAJE": {
        MetodoResolucion.DECISORIO: {
            "parametros": {
                "usuarioDecisorio": 46,
            },
        },
    },

    "SOLICITUD_PAGO_DIRECTO": {
        MetodoResolucion.DECISORIO: {
            "parametros": {
                "usuarioDecisorio": 46,
            },
        },
    },

    "SOLICITUD_REEMBOLSO": {
        MetodoResolucion.DECISORIO: {
            "parametros": {
                "usuarioDecisorio": 46,
            },
        },
    },

    "RENDICION_CUENTAS": {
      MetodoResolucion.DECISORIO: {
            "parametros": {
                "usuarioDecisorio": 46,
        },
    },
},
}


class ConfiguracionConsolidacionNoEncontrada(Exception):
    pass


class ConfiguracionConsolidacion:

    def obtener(self, tipo_solicitud, metodo_resolucion):
        configuraciones_tipo = CONFIGURACIONES.get(tipo_solicitud)

        if configuraciones_tipo is None:
            raise ConfiguracionConsolidacionNoEncontrada(
                f"No existe configuración de consolidación "
                f"para el tipo de solicitud: {tipo_solicitud}"
            )

        configuracion = configuraciones_tipo.get(metodo_resolucion)

        if configuracion is None:
            raise ConfiguracionConsolidacionNoEncontrada(
                f"No existe configuración para el método "
                f"{metodo_resolucion} y el tipo de solicitud "
                f"{tipo_solicitud}"
            )

        return ConfiguracionMetodo(
            metodo=metodo_resolucion,
            parametros=configuracion.get("parametros", {}),
        )
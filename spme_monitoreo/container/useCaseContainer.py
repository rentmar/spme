from dependency_injector import containers, providers
from ..domain.usecases.solicitudFondosUseCase import CrearSolicitudFondosUseCase
from ..domain.usecases.rendicionCuentasUseCase import CrearRendicionCuentasUseCase
from ..domain.usecases.solicitudReembolsoUseCase import CrearSolicitudReembolsoUseCase
from ..domain.usecases.solicitudViajeUseCase import CrearSolicitudViajeUseCase
from ..domain.usecases.solicitudPagoDirectoUseCase import CrearSolicitudPagoDirectoUseCase
from ..domain.usecases.obtenerDatosFormularioUseCase import ObtenerDatosFormularioUseCase

class CrearSolicitudFondosUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudFondosUseCase = providers.Singleton(CrearSolicitudFondosUseCase)

class CrearRendicionCuentasUseCaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    crearRendicionCuentasUseCase = providers.Singleton(CrearRendicionCuentasUseCase)

class CrearSolicitudReembolsoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudReembolsoUseCase = providers.Singleton(CrearSolicitudReembolsoUseCase)

class CrearSolicitudViajeUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudViajeUseCase = providers.Singleton(CrearSolicitudViajeUseCase)

class CrearSolicitudPagoDirectoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    crearSolicitudPagoDirectoUseCase = providers.Singleton(CrearSolicitudPagoDirectoUseCase)

class ObtenerDatosFormularioUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    obtenerDatosFormularioUseCase = providers.Singleton(ObtenerDatosFormularioUseCase)

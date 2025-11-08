from dependency_injector import containers, providers
from spme_monitoreo.domain.usecases.solicitudFondosUseCase import CrearSolicitudFondosUseCase
from spme_monitoreo.domain.usecases.rendicionCuentasUseCase import CrearRendicionCuentasUseCase
from spme_monitoreo.domain.usecases.solicitudReembolsoUseCase import CrearSolicitudReembolsoUseCase
from spme_monitoreo.domain.usecases.solicitudViajeUseCase import CrearSolicitudViajeUseCase
from spme_monitoreo.domain.usecases.solicitudPagoDirectoUseCase import CrearSolicitudPagoDirectoUseCase
from spme_monitoreo.domain.usecases.obtenerDatosFormularioUseCase import ObtenerDatosFormularioUseCase
from spme_monitoreo.domain.usecases.actualizarValidacionSolicitudFondosUseCase import ActualizarValidacionSolicitudFondosUseCase
from spme_monitoreo.domain.usecases.actualizarValidacionRendicionCuentasUseCase import ActualizarValidacionRendicionCuentasUseCase
from spme_monitoreo.domain.usecases.actualizarValidacionSolicitudReembolsoUseCase import ActualizarValidacionSolicitudReembolsoUseCase
from spme_monitoreo.domain.usecases.formaPagoUseCase import FormaPagoUseCase
from spme_monitoreo.domain.usecases.actualizarValidacionSolicitudViajeUseCase import ActualizarValidacionSolicitudViajeUseCase
from spme_monitoreo.domain.usecases.actualizarValidacionSolicitudPagoDirectoUseCase import ActualizarValidacionSolicitudPagoDirectoUseCase

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

class ActualizarValidacionSolicitudFondosUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudFondosUseCase = providers.Singleton(
        ActualizarValidacionSolicitudFondosUseCase
    )

class ActualizarValidacionRendicionCuentasUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    actualizarValidacionRendicionCuentasUseCase = providers.Singleton(
        ActualizarValidacionRendicionCuentasUseCase
    )

class ActualizarValidacionSolicitudReembolsoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudReembolsoUseCase = providers.Singleton(
        ActualizarValidacionSolicitudReembolsoUseCase
    )

class FormaPagoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    formaPagoUseCase = providers.Singleton(FormaPagoUseCase)

class ActualizarValidacionSolicitudViajeUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudViajeUseCase = providers.Singleton(
        ActualizarValidacionSolicitudViajeUseCase
    )

class ActualizarValidacionSolicitudPagoDirectoUseCaseContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    actualizarValidacionSolicitudPagoDirectoUseCase = providers.Singleton(
        ActualizarValidacionSolicitudPagoDirectoUseCase
    )
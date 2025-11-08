from dependency_injector import containers, providers
from spme_monitoreo.domain.repositories.solicitudFondosRepository import SolicitudFondosRepository
from spme_monitoreo.domain.repositories.rendicionCuentasRepository import RendicionCuentasRepository
from spme_monitoreo.domain.repositories.solicitudReembolsoRepository import SolicitudReembolsoRepository
from spme_monitoreo.domain.repositories.solicitudViajeRepository import SolicitudViajeRepository
from spme_monitoreo.domain.repositories.solicitudPagoDirectoRepository import SolicitudPagoDirectoRepository
from spme_monitoreo.domain.repositories.formaPagoRepository import FormaPagoRepository
from spme_monitoreo.domain.repositories.solicitudViajeRepository import SolicitudViajeRepository

class SolicitudFondosRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudFondosRepository = providers.Singleton(SolicitudFondosRepository)

class RendicionCuentasRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    rendicionCuentasRepository = providers.Singleton(RendicionCuentasRepository)

class SolicitudReembolsoRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudReembolsoRepository = providers.Singleton(SolicitudReembolsoRepository)

class SolicitudViajeRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudViajeRepository = providers.Singleton(SolicitudViajeRepository)

class SolicitudPagoDirectoRepositoryContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    solicitudPagoDirectoRepository = providers.Singleton(SolicitudPagoDirectoRepository)

class FormaPagoRepositoryContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()

    formaPagoRepository = providers.Singleton(FormaPagoRepository)

class FormaPagoRepositoryContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()

    formaPagoRepository = providers.Singleton(FormaPagoRepository)

class SolicitudViajeRepositoryContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()
    
    # Proveedor de dependencias
    solicitudViajeRepository = providers.Singleton(SolicitudViajeRepository)

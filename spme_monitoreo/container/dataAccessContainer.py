from dependency_injector import containers, providers
from ..dataaccess.solicitudFondosDataAccess import SolicitudFondosDataAccess

class SolicitudFondosDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos del SolicitudFondos.
    Proporciona una instancia de SolicitudFondosDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos del SolicitudFondos
    solicitudFondosDataAccess = providers.Singleton(SolicitudFondosDataAccess)
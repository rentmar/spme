from dependency_injector import containers, providers
from ..dataaccess.estructuraPeiDataAccess import EstructuracionPeiDataAccess

class EstructuracionPeiDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos del EstructuracionPei.
    Proporciona una instancia de EstructuracionPeiDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos del usuario
    estructuracionPeiDataAccess = providers.Singleton(EstructuracionPeiDataAccess)
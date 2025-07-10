from dependency_injector import containers, providers
from ..dataaccess.actividadesDataAccess import ActividadesDataAccess 

class ActividadesDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de Actividades.
    Proporciona una instancia de ActividadesDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de Actividades
    actividadesDataAccess = providers.Singleton(ActividadesDataAccess)
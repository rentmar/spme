from dependency_injector import containers, providers
from ..dataaccess.actividadesDataAccess import ActividadesDataAccess
from ..dataaccess.actividadTipoDataAccess import TipoActividadDataAccess 

class ActividadesDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de Actividades.
    Proporciona una instancia de ActividadesDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de Actividades
    actividadesDataAccess = providers.Singleton(ActividadesDataAccess)

class TipoActividadDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de Tipo de Actividad.
    Proporciona una instancia de TipoActividadDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos de Tipo de Actividad
    tipoActividadDataAccess = providers.Singleton(TipoActividadDataAccess)
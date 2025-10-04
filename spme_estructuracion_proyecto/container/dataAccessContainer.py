from dependency_injector import containers, providers
from ..dataaccess.proyectoDataAccess import ProyectoDataAccess

class ProyectoDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos de proyecto.
    Proporciona una instancia de ProyectoDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos del usuario
    proyectoDataAccess = providers.Singleton(ProyectoDataAccess)
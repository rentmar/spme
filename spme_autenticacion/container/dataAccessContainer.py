from dependency_injector import containers, providers
from ..dataaccess.userDataAccess import UserDataAccess

class UserDataAccessContainer(containers.DeclarativeContainer):
    """
    Contenedor de acceso a datos del usuario.
    Proporciona una instancia de UserDataAccess.
    """
    # Configuración del contenedor
    config = providers.Configuration()

    # Proveedor de acceso a datos del usuario
    userDataAccess = providers.Singleton(UserDataAccess)
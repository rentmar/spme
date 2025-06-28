from dependency_injector import containers, providers
from ..presenters.usuarioPresenter import UsuarioPresenter

class UsuarioPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    usuarioPresenter = providers.Factory(UsuarioPresenter)

    # Proveedor de dependencias para el usuarioPresenter con un request específico
    usuarioPresenterWithRequest = providers.Factory(
        UsuarioPresenter,
        userRequest=providers.Dependency(instance_of=dict)
    )
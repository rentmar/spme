from dependency_injector import containers, providers
from ..presenters.estructuracionPeiPresenter import EstructuracionPeiPresenter

class EstructuracionPeiPresenterContainer(containers.DeclarativeContainer):
    # Config del contenedor
    config = providers.Configuration()

    # Proveedor de dependencias
    estructuracionPeiPresenter = providers.Factory(EstructuracionPeiPresenter)

    # Proveedor de dependencias para el usuarioPresenter con un request específico
    # usuarioPresenterWithRequest = providers.Factory(
    #     UsuarioPresenter,
    #     userRequest=providers.Dependency(instance_of=dict)
    # )
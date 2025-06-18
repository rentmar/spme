from dependency_injector import containers, providers
from dataaccess.ObjetivoEspecificoDataAccess import ObjetivoEspecificoDataAccess

class ObjetivoEspecificoDataAccessContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    objetivoEspecificoDataAccess = providers.Singleton(ObjetivoEspecificoDataAccess)

from spme_estructuracion_pei.container.dataAccessContainer import EstructuracionPeiDataAccessContainer

class EstructuracionPeiRepository:
    
    def __init__(self):
        self.contenedor = EstructuracionPeiDataAccessContainer()
        self.estructuracionPeiDataAccess = self.contenedor.estructuracionPeiDataAccess()

    def createEstructuraPei(self, estructuraPei):
        """
        Crea un nuevo Estructuracion PEI.
        :param Estructuracion PEI: Objeto Estructuracion PEI a crear.
        :return: Estructuracion PEI creado.
        """
        return self.estructuracionPeiDataAccess.createEstructuraPei(estructuraPei)
    
    def obtenerEstructuraPei(self):
        
        return self.estructuracionPeiDataAccess.obtenerEstructuraPei()
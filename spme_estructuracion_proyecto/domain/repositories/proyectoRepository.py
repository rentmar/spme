from spme_estructuracion_proyecto.container.dataAccessContainer import ProyectoDataAccessContainer

class ProyectoRepository:

    def __init__(self):
        self.contenedor = ProyectoDataAccessContainer()
        self.proyectoDataAccess = self.contenedor.proyectoDataAccess()

    def numeroProyectos(self):

        return self.proyectoDataAccess.numeroProyectos()
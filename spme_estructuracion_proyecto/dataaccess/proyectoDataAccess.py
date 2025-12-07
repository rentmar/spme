from ..models import Proyecto

class ProyectoDataAccess:
    """
    Clase para acceder a los datos del usuario.
    """
    def numeroProyectosEjecucion(self):
        """
        Obtiene el numero proyectos ejecucion.

        :return: Total de numero proyectos.
        """
        return Proyecto.objects.filter(estado="PL").count()

    def numeroProyectos(self):
        """
        Obtiene el numero proyectos totales.

        :return: Total de numero proyectos.
        """
        return Proyecto.objects.count()
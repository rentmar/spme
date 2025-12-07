from ..models import EstructuraPei

class EstructuracionPeiDataAccess:
    """
    Clase para acceder a los datos del usuario.
    """
    def __init__(self):
        pass
    
    def createEstructuraPei(self, estructuraPei):
        """
        Crea un nuevo estructuraPei.
        :param estructuraPei: Objeto estructuraPei a crear.
        :return: estructuraPei creado.
        """
        return EstructuraPei.objects.create(
            titulo=estructuraPei['titulo'],
            descripcion = estructuraPei['descripcion'],
            fecha_creacion = estructuraPei['fecha_creacion'],
            fecha_inicio = estructuraPei['fecha_inicio'],
            fecha_fin = estructuraPei['fecha_fin'],
            esta_vigente = estructuraPei['esta_vigente'],
            creado_el = estructuraPei['creado_el'],
            modificado_el = estructuraPei['modificado_el'],
        )
    
    def obtenerEstructuraPei(self):
        return EstructuraPei.objects.all().first()

    def numeroPeiVigente(self):
        """
        Obtiene el numero total de Pei Vigente.

        :return: Total de actividades finalizadas .
        """
        return EstructuraPei.objects.filter(esta_vigente=True).count()

    def numeroTotalPei(self):
        """
        Obtiene el numero total de Pei.

        :return: Total de actividades finalizadas.
        """
        return EstructuraPei.objects.count()
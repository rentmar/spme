from ..models import EstructuraPei

class EstructuracionPeiDataAccess:
    """
    Clase para acceder a los datos del usuario.
    """
    def __init__(self):
        pass

    # def getUserByName(self, userName):
    #     """
    #     Obtiene un usuario por su nombre de usuario.
    #     :param user_name: Nombre de usuario a buscar.
    #     :return: Usuario encontrado o None si no existe.
    #     """
    #     return Usuario.objects.filter(usuario=userName).first()
    
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
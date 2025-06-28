from ..models import Usuario

class UserDataAccess:
    """
    Clase para acceder a los datos del usuario.
    """
    def __init__(self):
        pass

    def getUserByName(self, userName):
        """
        Obtiene un usuario por su nombre de usuario.
        :param user_name: Nombre de usuario a buscar.
        :return: Usuario encontrado o None si no existe.
        """
        return Usuario.objects.filter(usuario=userName).first()
    
    def createUser(self, user):
        """
        Crea un nuevo usuario.
        :param user: Objeto Usuario a crear.
        :return: Usuario creado.
        """
        return Usuario.objects.create(
            usuario=user.usuario.value,
            password=user.password.value,
            permisos=user.permisos.value
        )
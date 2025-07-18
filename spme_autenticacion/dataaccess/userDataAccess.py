from ..models import Usuario

class UserDataAccess:
    """
    Clase para acceder a los datos del usuario.
    """
    def __init__(self):
        pass

    def autenticarUsuario(self, userName, password):
        """
        Autentica un usuario por su nombre de usuario y contraseña.
        :param userName: Nombre de usuario.
        :param password: Contraseña del usuario.
        :return: Usuario autenticado o None si no existe.
        """
        usuario = Usuario.objects.filter(username=userName).first()
        if usuario and usuario.check_password(password):
            return usuario
        return None

    def usuarioPorUsername(self, userName):
        """
        Obtiene un usuario por su nombre de usuario.
        :param user_name: Nombre de usuario a buscar.
        :return: Usuario encontrado o None si no existe.
        """
        print(f"Buscando usuario por nombre: {userName}")
        usuario = Usuario.objects.get(username=userName)
        print(f"Usuario encontrado: {usuario}")
        if usuario is not None:
            return usuario
        return None
        
    def createUser(self, user):
        """
        Crea un nuevo usuario.
        :param user: Objeto Usuario a crear.
        :return: Usuario creado.
        """
        return Usuario.objects.create(
            username=user.username.value,
            password=user.password.value,
            permisos=user.permisos.value
        )
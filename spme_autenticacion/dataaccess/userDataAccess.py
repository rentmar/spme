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
        
    def createUser(self, userData):
        """
        Crea un nuevo usuario.
        :param user: Objeto Usuario a crear.
        :return: Usuario creado.
        """
        if Usuario.objects.filter(username=userData["username"]).exists():
            return None

        return Usuario.objects.create_user(
            username=userData["username"],
            password=userData["password"],  
            nombre=userData["nombre"],
            paterno=userData["paterno"],
            materno=userData["materno"],
            ci=userData["materno"],
            cargo=userData["ci"],
            banco=userData["banco"],
            numero_cuenta=userData["numero_cuenta"],
            tipo_cuenta=userData["tipo_cuenta"],
            is_active=userData["is_active"],
            permisos=userData["permisos"],
            is_staff=userData.get("is_staff", True),
            is_superuser=userData.get("is_superuser", False)
        )

    def obtenerListaUsuarios(self):
        """
        Obtiene la lista de usuarios.
        :return: Lista de usuarios.
        """
        return Usuario.objects.filter(is_superuser=False, is_active=True)
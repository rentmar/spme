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
        usuario = Usuario.objects.filter(is_active=True,username=userName).values('id','nombre','paterno','materno','cargo','permisos','ci','banco','numero_cuenta').first()

        if usuario:
            return usuario
        return None

    def nombreUsuarioPorId(self, userId):
        """
        Obtiene el nombre de un usuario por su ID.
        :param userId: ID del usuario a buscar.
        :return: Nombre del usuario encontrado o None si no existe.
        """
        usuario = Usuario.objects.filter(id=userId).values('nombre','paterno','materno').first()
        if usuario:
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
            ci=userData["ci"],
            cargo=userData["cargo"],
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

    def obtenerListaValidadores(self):
        """
        Obtiene la lista de validadores.
        :return: Lista de validadores.
        """
        return Usuario.objects.filter(is_active=True,is_superuser=False).values('id','nombre','paterno','materno','cargo')
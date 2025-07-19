from spme_autenticacion.container.dataAccessContainer import UserDataAccessContainer

class UserRepository:
    
    def __init__(self):
        self.contenedor = UserDataAccessContainer()
        self.userDataAccess = self.contenedor.userDataAccess()

    def obtenerUsuarioPorUsername(self, userName):
        """
        Obtiene un usuario por su Nombre.
        :param user_name: Nombre del usuario a buscar.
        :return: Usuario encontrado o None si no existe.
        """
        return self.userDataAccess.usuarioPorUsername(userName)
        
    def createUser(self, userRequest):
        """
        Crea un nuevo usuario.
        :param user: Objeto Usuario a crear.
        :return: Usuario creado.
        """
        return self.userDataAccess.createUser(userRequest)

    def autenticarUsuario(self,userRequest):
        """
        Autentica un usuario por su nombre de usuario y contraseña.
        :param userName: Nombre de usuario.
        :param password: Contraseña del usuario.
        :return: Usuario autenticado o None si no existe.
        """
        return self.userDataAccess.autenticarUsuario(userRequest['username'], userRequest['password'])
    
    def obtenerListaUsuarios(self):
        """
        Obtiene la lista de usuarios.
        :return: Lista de usuarios.
        """
        return self.userDataAccess.obtenerListaUsuarios()
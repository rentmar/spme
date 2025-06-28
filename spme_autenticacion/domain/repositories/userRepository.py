from spme_autenticacion.container.dataAccessContainer import UserDataAccessContainer

class UserRepository:
    
    def __init__(self):
        self.contenedor = UserDataAccessContainer()
        self.userDataAccess = self.contenedor.userDataAccess()

    def getUserByName(self, userName):
        """
        Obtiene un usuario por su Nombre.
        :param user_name: Nombre del usuario a buscar.
        :return: Usuario encontrado o None si no existe.
        """
        user = self.userDataAccess.getUserByName(userName)
        if user is not None:
            return user 
        else:
            return None
        
    def createUser(self, userEntity):
        """
        Crea un nuevo usuario.
        :param user: Objeto Usuario a crear.
        :return: Usuario creado.
        """
        return self.userDataAccess.createUser(userEntity)
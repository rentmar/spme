from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme_autenticacion.common.MessageManager import MessageType
from .domain.models.request.userRequest import ObtenerUsuarioRequest, CrearUsuarioRequest, AutenticacionUsuarioRequest
from .domain.models.response.userResponse import UsuarioResponse, CreateUserResponse, AutenticacionUsuarioResponse
from .domain.models.response.userResponse import ListaValidadoresResponse
from .container.presenterContainer import UsuarioPresenterContainer

class ObtenerUsuario(APIView):
    """
    API view obtener usuario.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def post(self, request, *args, **kwargs):
        
        obtenerUsuarioRequestRequest = ObtenerUsuarioRequest(data=request.data)

        if obtenerUsuarioRequestRequest.is_valid():

            usuarioResponse = self.usurioPresenter.obtenerUsuario(obtenerUsuarioRequestRequest.validated_data)

            response =  UsuarioResponse(data=usuarioResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                return Response({"mensaje": MessageType.NOT_FOUND.value}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class CrearUsuario(APIView):
    """
    API view crear usuario.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def post(self, request, *args, **kwargs):
        
        userRequest = CrearUsuarioRequest(data=request.data)

        if userRequest.is_valid():

            createResponse = self.usurioPresenter.createUsuario(userRequest.validated_data)

            response = CreateUserResponse(data=createResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class AutenticacionUsuario(APIView):
    """
    API view autenticación usuario.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def post(self, request, *args, **kwargs):

        userRequest = AutenticacionUsuarioRequest(data=request.data)

        if userRequest.is_valid():

            userResponse = self.usurioPresenter.autenticarUsuario(userRequest.validated_data)

            response = AutenticacionUsuarioResponse(data=userResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                return Response({"estado": MessageType.UNAUTHORIZED.value}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class ListaUsuarios(APIView):
    """
    API view lista usuarios.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def get(self, request, *args, **kwargs):
        """
        Obtiene la lista de usuarios.
        """
        listResponse = self.usurioPresenter.obtenerListaUsuarios()

        print("ListResponse:", listResponse)

        listaUsuarios = {
            "usuarios": [
                {
                    "id": 1,
                    "usuario": "Will Smith"
                },
                {
                    "id": 2,
                    "usuario": "Gorg Selva"
                },
                {
                    "id": 3,
                    "usuario": "Jaime Dunn"
                }
            ]
        }
        return Response(listaUsuarios, status=status.HTTP_200_OK)
    
class ListaValidadores(APIView):
    """
    API view lista validadores.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def get(self, request, *args, **kwargs):
        """
        Obtiene la lista de validadores.
        """
        listResponse = self.usurioPresenter.obtenerListaValidadores()

        response = ListaValidadoresResponse(data=listResponse)
        if response.is_valid():
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

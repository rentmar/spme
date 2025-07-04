from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme_autenticacion.common.MessageManager import MessageType
from .domain.models.request.userRequest import GetUserRequest, CreateUserRequest
from .domain.models.response.userResponse import UserResponse, CreateUserResponse
from .container.presenterContainer import UsuarioPresenterContainer

class GetUserByName(APIView):
    """
    API view obtener usuario.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def get(self, request, *args, **kwargs):
        
        getUserRequest = GetUserRequest(data=request.data)

        if(getUserRequest.is_valid()):

            response = self.usurioPresenter.getUsuario(getUserRequest.validated_data)

            userResponse =  UserResponse(data=response)

            if userResponse.is_valid():
                return Response(userResponse.data, status=status.HTTP_200_OK)
            else:
                return Response({"mensaje": MessageType.NOT_FOUND.value}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class CreateUser(APIView):
    """
    API view crear usuario.
    """
    def __init__(self):
        self.contenedor = UsuarioPresenterContainer()
        self.usurioPresenter = self.contenedor.usuarioPresenter()

    def post(self, request, *args, **kwargs):
        
        userRequest = CreateUserRequest(data=request.data)

        if userRequest.is_valid():

            createResponse = self.usurioPresenter.createUsuario(userRequest)

            response = CreateUserResponse(data=createResponse)

            if response.is_valid() and response.data['id'] is not None:
                response.data['mensaje'] = MessageType.SUCCESS.value
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": MessageType.ERROR.value}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .common.MessageManager import MessageType
from .domain.models.request.actividadesRequest import ObtenerActividadesUsuarioRequest
from .domain.models.response.actividadesResponse import ActividadesUsuarioResponse
from .container.presenterContainer import ActividadesPresenterContainer

class ObtenerActividadesUsuario(APIView):
    """
    API para obtener las actividades de un usuario
    """
    def __init__(self):
        self.contenedor = ActividadesPresenterContainer()
        self.actividades_presenter = self.contenedor.actividadesPresenter()

    def post(self, request, *args, **kwargs):
        
        obtenerActividadesUsuarioRequest = ObtenerActividadesUsuarioRequest(data=request.data)

        if obtenerActividadesUsuarioRequest.is_valid():

            actividadesUsuario = self.actividades_presenter.obtenerActividadesUsuario(obtenerActividadesUsuarioRequest.validated_data)

            response = ActividadesUsuarioResponse(data = actividadesUsuario)

            if response.is_valid():
                return Response(response.data,status=status.HTTP_200_OK)
            else:
                return Response({"mensaje": MessageType.NOT_FOUND.value},status = status.HTTP_404_NOT_FOUND)

        
        else: 
             return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
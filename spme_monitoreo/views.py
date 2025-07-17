from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme.common.MessageManager import MessageType
from .container.presenterContainer import SolicitudFondosPresenterContainer
from .domain.models.request.solicitudFondosRequest import CrearSolicitudFondosRequest
from .domain.models.response.solicitudFondosResponse import CreateSolicitudFondosResponse

class SolicitudFondos(APIView):
    """
    API para solicitud de fondos
    """
    def __init__(self):
        self.contenedor = SolicitudFondosPresenterContainer()
        self.solicitudFondosPresenter = self.contenedor.solicitudFondosPresenter()

    def post(self, request, *args, **kwargs):
        
        createSolicitudFondosRequest = CrearSolicitudFondosRequest(data=request.data)

        if createSolicitudFondosRequest.is_valid():
            
            solicitudFondosResponse = self.solicitudFondosPresenter.crearSolicitudFondos(createSolicitudFondosRequest.validated_data)

            response = CreateSolicitudFondosResponse(data=solicitudFondosResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
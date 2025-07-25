from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme.common.MessageManager import MessageType
from .container.presenterContainer import SolicitudFondosPresenterContainer,RendicionCuentasPresenterContainer,SolicitudReembolsoPresenterContainer
from .domain.models.request.solicitudFondosRequest import CrearSolicitudFondosRequest
from .domain.models.response.solicitudFondosResponse import CreateSolicitudFondosResponse
from .domain.models.request.rendicionCuentasRequest import CrearRendicionCuentasRequest
from .domain.models.response.rendicionCuentasResponse import CreateRendicionFondosResponse
from .domain.models.request.solicitudReembolsoRequest import CrearSolicitudReembolsoRequest
from .domain.models.response.solicitudReembolsoResponse import CreateSolicitudReembolsoResponse

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
    
class RendicionCuentas(APIView):
    """
    API para rendición de cuentas
    """
    def __init__(self):
        self.contenedor = RendicionCuentasPresenterContainer()
        self.rendicionCuentasPresenter = self.contenedor.rendicionCuentasPresenterPresenter()

    def post(self, request, *args, **kwargs):
        
        createRendicionCuentasRequest = CrearRendicionCuentasRequest(data=request.data)

        if createRendicionCuentasRequest.is_valid():
            
            rendicionCuentasResponse = self.rendicionCuentasPresenter.crearRendicionCuentas(createRendicionCuentasRequest.validated_data)

            response = CreateRendicionFondosResponse(data=rendicionCuentasResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class SolicitudReembolso(APIView):
    """
    API para solicitud de reembolso
    """
    def __init__(self):
        self.contenedor = SolicitudReembolsoPresenterContainer()
        self.solicitudReembolsoPresenter = self.contenedor.solicitudReembolsoPresenter()

    def post(self, request, *args, **kwargs):
        
        createSolicitudReembolsoRequest = CrearSolicitudReembolsoRequest(data=request.data)

        if createSolicitudReembolsoRequest.is_valid():
            
            solicitudReembolsoResponse = self.solicitudReembolsoPresenter.crearSolicitudFondos(createSolicitudReembolsoRequest.validated_data)

            response = CreateSolicitudReembolsoResponse(data=solicitudReembolsoResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"mensaje": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"mensaje": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
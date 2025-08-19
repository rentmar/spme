from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme.common.MessageManager import MessageType
from .container.presenterContainer import SolicitudFondosPresenterContainer,RendicionCuentasPresenterContainer,SolicitudReembolsoPresenterContainer,SolicitudViajePresenterContainer,SolicitudPagoDirectoPresenterContainer,DatosFormularioPresenterContainer
from .domain.models.request.solicitudFondosRequest import CrearSolicitudFondosRequest
from .domain.models.response.solicitudFondosResponse import CreateSolicitudFondosResponse
from .domain.models.request.rendicionCuentasRequest import CrearRendicionCuentasRequest
from .domain.models.response.rendicionCuentasResponse import CreateRendicionFondosResponse
from .domain.models.request.solicitudReembolsoRequest import CrearSolicitudReembolsoRequest
from .domain.models.response.solicitudReembolsoResponse import CreateSolicitudReembolsoResponse
from .domain.models.request.solicitudViajeRequest import CrearSolicitudViajeRequest
from .domain.models.response.solicitudViajeResponse import CreateSolicitudViajeResponse
from .domain.models.request.solicitudPagoDirectoRequest import CrearSolicitudPagoDirectoRequest
from .domain.models.response.solicitudPagoDirectoResponse import CreateSolicitudPagoDirectoResponse
from .domain.models.request.datosFormRequest import ObtenerDatosFormularioRequest
from .domain.models.response.obtenerDatosFormResponse import ObtenerDatosFormularioResponse

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
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class SolicitudViaje(APIView):
    """
    API para solicitud de viaje
    """
    def __init__(self):
        self.contenedor = SolicitudViajePresenterContainer()
        self.solicitudViajePresenter = self.contenedor.solicitudViajePresenter()

    def post(self, request, *args, **kwargs):

        createSolicitudViajeRequest = CrearSolicitudViajeRequest(data=request.data)

        if createSolicitudViajeRequest.is_valid():

            solicitudViajeResponse = self.solicitudViajePresenter.crearSolicitudViaje(createSolicitudViajeRequest.validated_data)

            response = CreateSolicitudViajeResponse(data=solicitudViajeResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

class SolicitudPagoDirecto(APIView):
    """
    API para solicitud de pago directo
    """
    def __init__(self):
        self.contenedor = SolicitudPagoDirectoPresenterContainer()
        self.solicitudPagoDirectoPresenter = self.contenedor.solicitudPagoDirectoPresenter()

    def post(self, request, *args, **kwargs):

        createSolicitudPagoDirectoRequest = CrearSolicitudPagoDirectoRequest(data=request.data)

        if createSolicitudPagoDirectoRequest.is_valid():

            solicitudPagoDirectoResponse = self.solicitudPagoDirectoPresenter.crearSolicitudPagoDirecto(createSolicitudPagoDirectoRequest.validated_data)

            response = CreateSolicitudPagoDirectoResponse(data=solicitudPagoDirectoResponse)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

class ObtenerDatosFormulario(APIView):
    """
    API para datos del formulario
    """
    def __init__(self):
        self.contenedor = DatosFormularioPresenterContainer()
        self.datosFormularioPresenter = self.contenedor.datosFormularioPresenter()

    def post(self, request, *args, **kwargs):

        obtenerDatosFormularioRequest = ObtenerDatosFormularioRequest(data=request.data)

        if obtenerDatosFormularioRequest.is_valid():

            datosFormularioResponse = self.datosFormularioPresenter.obtenerDatosFormulario(obtenerDatosFormularioRequest.validated_data)
           
            response = ObtenerDatosFormularioResponse(data=datosFormularioResponse)
            
            if response.is_valid():
                return Response(response.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
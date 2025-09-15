from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .common.MessageManager import MessageType
from .domain.models.request.actividadesRequest import ObtenerActividadIdRequest,CrearActividadRequest,ObtenerActividadesUsuarioRequest,ObtenerEncabezadoPorIdRequest
from .domain.models.response.actividadesResponse import ActividadesUsuarioResponse,ActividadesGanttResponse,CrearActividadResponse,ObtenerActividadIdResponse,ObtenerEncabezadoActividadResponse
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

class CrearActividad(APIView):
    """
    API para crear actividad 
    """
    def __init__(self):
        self.contenedor = ActividadesPresenterContainer()
        self.actividadesPresenter = self.contenedor.actividadesPresenter()

    def post(self, request, *args, **kwargs):
        
        crearActividadRequest = CrearActividadRequest(data=request.data)

        if crearActividadRequest.is_valid():

            crearActividadResponse = self.actividadesPresenter.crearActividad(crearActividadRequest.validated_data)

            response = CrearActividadResponse(data = crearActividadResponse)

            if response.is_valid():
                return Response(response.data,status=status.HTTP_200_OK)
            else:
                return Response({"estado": MessageType.NOT_FOUND.value},status = status.HTTP_404_NOT_FOUND)
            
        else: 
             return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

class ObtenerActividadesGantt(APIView):
    """
    API para obtener las actividades del diagrama de Gantt
    """
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def __init__(self):
        self.contenedor = ActividadesPresenterContainer()
        self.actividadesPresenter = self.contenedor.actividadesPresenter()

    def post(self, request, *args, **kwargs):

        requestActividadesGantt = ObtenerActividadesUsuarioRequest(data=request.data)

        if requestActividadesGantt.is_valid():

            actividadesGantt = self.actividadesPresenter.obtenerActividadesGantt(requestActividadesGantt.validated_data)

            response = ActividadesGanttResponse(data=actividadesGantt)
           
            if response.is_valid():
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                print("Serializer Errors:", response.errors)
                return Response({"estado": MessageType.NOT_FOUND.value}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

class ObtenerActividadId(APIView):
    """
    API para obtener una actividad por su ID
    """
    def __init__(self):
        self.contenedor = ActividadesPresenterContainer()
        self.actividadesPresenter = self.contenedor.actividadesPresenter()

    def post(self, request, *args, **kwargs):

        obtenerActividadIdRequest = ObtenerActividadIdRequest(data=request.data)

        if obtenerActividadIdRequest.is_valid():

            actividad = self.actividadesPresenter.obtenerActividadPorId(obtenerActividadIdRequest.validated_data)

            response = ObtenerActividadIdResponse(data=actividad)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                return Response({"estado": MessageType.NOT_FOUND.value}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

class ObtenerEncabezadoActividad(APIView):
    """
    API para obtener el encabezado de una actividad
    """
    def __init__(self):
        self.contenedor = ActividadesPresenterContainer()
        self.actividadesPresenter = self.contenedor.actividadesPresenter()

    def post(self, request, *args, **kwargs):

        obtenerEncabezadoActividadRequest = ObtenerEncabezadoPorIdRequest(data=request.data)

        if obtenerEncabezadoActividadRequest.is_valid():

            encabezado = self.actividadesPresenter.obtenerEncabezadoActividadPorId(obtenerEncabezadoActividadRequest.validated_data)
            
            response = ObtenerEncabezadoActividadResponse(data=encabezado)

            if response.is_valid():
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                print("Serializer Errors:", response.errors)
                return Response({"estado": MessageType.NOT_FOUND.value}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)

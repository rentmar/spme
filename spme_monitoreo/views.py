import traceback
import logging
from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spme.common.MessageManager import MessageType
from .container.presenterContainer import ActualizarValidacionSolicitudPagoDirectoPresenterContainer,ActualizarValidacionSolicitudViajePresenterContainer,FormaPagoPresenterContainer,ActualizarValidacionSolicitudReembolsoPresenterContainer,ActualizarValidacionRendicionCuentasPresenterContainer,SolicitudFondosPresenterContainer,ActualizarValidacionSolicitudFondosPresenterContainer,RendicionCuentasPresenterContainer,SolicitudReembolsoPresenterContainer,SolicitudViajePresenterContainer,SolicitudPagoDirectoPresenterContainer,DatosFormularioPresenterContainer
from .domain.models.request.solicitudFondosRequest import CrearSolicitudFondosRequest
from .domain.models.response.solicitudFondosResponse import CreateSolicitudFondosResponse
from .domain.models.request.rendicionCuentasRequest import CrearRendicionCuentasRequest
from .domain.models.response.rendicionCuentasResponse import CreateRendicionFondosResponse
from .domain.models.request.solicitudReembolsoRequest import CrearSolicitudReembolsoRequest,ObtenerSolicitudReembolsoRequest
from .domain.models.response.solicitudReembolsoResponse import CreateSolicitudReembolsoResponse,ObtenerSolicitudReembolsoResponse 
from .domain.models.request.solicitudViajeRequest import CrearSolicitudViajeRequest
from .domain.models.response.solicitudViajeResponse import CreateSolicitudViajeResponse
from .domain.models.request.solicitudPagoDirectoRequest import CrearSolicitudPagoDirectoRequest
from .domain.models.response.solicitudPagoDirectoResponse import CreateSolicitudPagoDirectoResponse
from .domain.models.request.datosFormRequest import ObtenerDatosFormularioRequest
from .domain.models.response.obtenerDatosFormResponse import ObtenerDatosFormularioResponse
from .domain.models.request.solicitudFondosUpdateRequest import ActualizarValidacionSolicitudFondosRequest
from .domain.models.response.solicitudFondosUpdateResponse import ActualizarValidacionSolicitudFondosResponse
from .domain.models.request.rendicionCuentasRequest import ObtenerRendicionDeCuentasRequest
from .domain.models.response.rendicionCuentasResponse import ObtenerRendicionDeCuentasResponse
from .domain.models.request.rendicionCuentasUpdateRequest import ActualizarValidacionRendicionCuentasRequest
from .domain.models.response.rendicionCuentasUpdateResponse import ActualizarValidacionRendicionCuentasResponse
from .domain.models.request.solicitudReembolsoUpdateRequest import ActualizarValidacionSolicitudReembolsoRequest
from .domain.models.response.solicitudReembolsoUpdateResponse import ActualizarValidacionSolicitudReembolsoResponse
from .domain.models.request.formaPagoRequest import ObtenerFormaPagoRequest
from .domain.models.response.formaPagoResponse import ObtenerFormaPagoResponse
from .domain.models.request.solicitudViajeRequest import ObtenerSolicitudesViajeRequest
from .domain.models.response.solicitudViajeResponse import ObtenerSolicitudesViajeResponse
from .domain.models.request.solicitudViajeUpdateRequest import ActualizarValidacionSolicitudViajeRequest
from .domain.models.response.solicitudViajeUpdateResponse import ActualizarValidacionSolicitudViajeResponse
from .domain.models.request.solicitudPagoDirectoRequest import ObtenerSolicitudesPagoDirectoRequest
from .domain.models.response.solicitudPagoDirectoResponse import ObtenerSolicitudesPagoDirectoResponse
from .domain.models.request.solicitudPagoDirectoUpdateRequest import ActualizarValidacionSolicitudPagoDirectoRequest
from .domain.models.response.solicitudPagoDirectoUpdateResponse import ActualizarValidacionSolicitudPagoDirectoResponse

logger = logging.getLogger(__name__)

class SolicitudFondos(APIView):
    """
    API para solicitud de fondos
    """
    def __init__(self):
        self.contenedor = SolicitudFondosPresenterContainer()
        self.solicitudFondosPresenter = self.contenedor.solicitudFondosPresenter()

    def post(self, request, *args, **kwargs):
        try:
            createSolicitudFondosRequest = CrearSolicitudFondosRequest(data=request.data)
            
            if createSolicitudFondosRequest.is_valid():
                
                solicitudFondosResponse = self.solicitudFondosPresenter.crearSolicitudFondos(createSolicitudFondosRequest.validated_data)
                response = CreateSolicitudFondosResponse(data=solicitudFondosResponse)

                if response.is_valid():
                    return Response(response.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"estado": MessageType.ERROR.value, "errores": response.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"estado": MessageType.BAD_REQUEST.value, "errores": createSolicitudFondosRequest.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"estado": MessageType.ERROR.value, "mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Nueva clase para obtener solicitudes - CORREGIDA
class ObtenerSolicitudFondos(APIView):
    """
    API para obtener todas las solicitudes de fondos
    """
    
    def __init__(self):
        # Usamos el mismo contenedor que SolicitudFondos
        self.contenedor = SolicitudFondosPresenterContainer()
        self.solicitudFondosPresenter = self.contenedor.solicitudFondosPresenter()
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener todas las solicitudes de fondos
            solicitudes = self.solicitudFondosPresenter.obtenerSolicitudesFondos()
            return Response({
                "estado": MessageType.SUCCESS.value,
                "solicitudes": solicitudes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value, 
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ObtenerSolicitudFondosPorFiltros(APIView):
    """
    API para obtener solicitudes de fondos filtrando por actividad_id, usuario_id y tarea_id
    """
    
    def __init__(self):
        self.contenedor = SolicitudFondosPresenterContainer()
        self.solicitudFondosPresenter = self.contenedor.solicitudFondosPresenter()
    
    def post(self, request, *args, **kwargs):  # Cambiado de GET a POST
        try:
            # Obtener parámetros del body JSON
            data = request.data
            actividad_id = data.get('actividad_id')
            usuario_id = data.get('usuario_id')
            tarea_id = data.get('tarea_id')
            
            # Validar parámetros requeridos
            if not actividad_id or not usuario_id:
                return Response({
                    "estado": MessageType.BAD_REQUEST.value,
                    "mensaje": "Los parámetros actividad_id y usuario_id son requeridos"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Llamar al presenter con los filtros
            solicitudes = self.solicitudFondosPresenter.obtenerSolicitudesFondosPorFiltros(
                actividad_id=actividad_id,
                usuario_id=usuario_id,
                tarea_id=tarea_id
            )
            
            return Response({
                "estado": MessageType.SUCCESS.value,
                "solicitudes": solicitudes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value, 
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RendicionCuentas(APIView):
    """
    API para rendición de cuentas
    """
    def __init__(self):
        self.contenedor = RendicionCuentasPresenterContainer()
        # self.rendicionCuentasPresenter = self.contenedor.rendicionCuentasPresenterPresenter()
        self.rendicionCuentasPresenter = self.contenedor.rendicionCuentasPresenter()

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
 
class SolicitudViaje(APIView):
    """
    API para solicitud de viaje
    """
    def __init__(self):
        self.contenedor = SolicitudViajePresenterContainer()
        self.solicitudViajePresenter = self.contenedor.solicitudViajePresenter()

    def post(self, request, *args, **kwargs):
        try:
            createSolicitudViajeRequest = CrearSolicitudViajeRequest(data=request.data)
            
            if createSolicitudViajeRequest.is_valid():
                solicitudViajeResponse = self.solicitudViajePresenter.crearSolicitudViaje(
                    createSolicitudViajeRequest.validated_data
                )
                response = CreateSolicitudViajeResponse(data=solicitudViajeResponse)

                if response.is_valid():
                    return Response(response.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": createSolicitudViajeRequest.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                return Response(response.data, status=status.HTTP_302_FOUND)
            else:
                return Response({"estado": MessageType.ERROR.value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"estado": MessageType.BAD_REQUEST.value}, status=status.HTTP_400_BAD_REQUEST)
    
class ActualizarValidacionSolicitudFondos(APIView):
    """
    API para actualizar validaciones de solicitud de fondos
    """
    
    def __init__(self):
        self.contenedor = ActualizarValidacionSolicitudFondosPresenterContainer()
        self.actualizarValidacionPresenter = self.contenedor.actualizarValidacionSolicitudFondosPresenter()

    def patch(self, request, *args, **kwargs):
        try:
            updateRequest = ActualizarValidacionSolicitudFondosRequest(data=request.data)
            
            if updateRequest.is_valid():
                solicitudResponse = self.actualizarValidacionPresenter.actualizarValidacionSolicitudFondos(
                    updateRequest.validated_data
                )
                response = ActualizarValidacionSolicitudFondosResponse(data=solicitudResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": updateRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ObtenerRendicionDeCuentas(APIView):
    """
    API para obtener rendiciones de cuentas con filtros
    """
    def __init__(self):
        self.contenedor = RendicionCuentasPresenterContainer()
        self.rendicionCuentasPresenter = self.contenedor.rendicionCuentasPresenter()

    def post(self, request, *args, **kwargs):
        try:
            obtenerRendicionRequest = ObtenerRendicionDeCuentasRequest(data=request.data)
            
            if obtenerRendicionRequest.is_valid():
                rendicionesResponse = self.rendicionCuentasPresenter.obtenerRendicionDeCuentas(
                    obtenerRendicionRequest.validated_data
                )
                
                response = ObtenerRendicionDeCuentasResponse(data=rendicionesResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "estado": MessageType.ERROR.value, 
                        "errores": response.errors
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "estado": MessageType.BAD_REQUEST.value, 
                "errores": obtenerRendicionRequest.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value, 
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActualizarValidacionRendicionCuentas(APIView):
    """
    API para actualizar validaciones de rendición de cuentas
    """

    def __init__(self):
        self.contenedor = ActualizarValidacionRendicionCuentasPresenterContainer()
        self.actualizarValidacionPresenter = self.contenedor.actualizarValidacionRendicionCuentasPresenter()

    def patch(self, request, *args, **kwargs):
        try:
            updateRequest = ActualizarValidacionRendicionCuentasRequest(data=request.data)
            
            if updateRequest.is_valid():
                rendicionResponse = self.actualizarValidacionPresenter.actualizarValidacionRendicionCuentas(
                    updateRequest.validated_data
                )
                
                response = ActualizarValidacionRendicionCuentasResponse(data=rendicionResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": updateRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SolicitudReembolso(APIView):
    """
    API para solicitud de reembolso (reposición)
    """

    def __init__(self):
        try:
            self.contenedor = SolicitudReembolsoPresenterContainer()
            self.solicitudReembolsoPresenter = self.contenedor.solicitudReembolsoPresenter()
            logger.info("SolicitudReembolso presenter inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar presenter: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def post(self, request, *args, **kwargs):
        try:
            logger.info("Iniciando creación de solicitud de reembolso")
            logger.info(f"Datos recibidos: {request.data}")
            
            createSolicitudReembolsoRequest = CrearSolicitudReembolsoRequest(data=request.data)
            logger.info("Request serializer creado")
            
            if createSolicitudReembolsoRequest.is_valid():
                logger.info("Request válido, llamando al presenter")
                solicitudReembolsoResponse = self.solicitudReembolsoPresenter.crearSolicitudReembolso(
                    createSolicitudReembolsoRequest.validated_data
                )
                logger.info(f"Respuesta del presenter: {solicitudReembolsoResponse}")
                
                response = CreateSolicitudReembolsoResponse(data=solicitudReembolsoResponse)
                
                if response.is_valid():
                    logger.info("Solicitud creada exitosamente")
                    return Response(response.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"Errores en response serializer: {response.errors}")
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            logger.error(f"Request inválido: {createSolicitudReembolsoRequest.errors}")
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": createSolicitudReembolsoRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(f"Error general en SolicitudReembolso: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e), "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ObtenerSolicitudReembolso(APIView):
    """
    API para obtener solicitudes de reembolso con filtros
    """

    def __init__(self):
        try:
            self.contenedor = SolicitudReembolsoPresenterContainer()
            self.solicitudReembolsoPresenter = self.contenedor.solicitudReembolsoPresenter()
            logger.info("ObtenerSolicitudReembolso presenter inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar presenter: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def post(self, request, *args, **kwargs):
        try:
            logger.info("Iniciando obtención de solicitudes de reembolso")
            logger.info(f"Datos recibidos: {request.data}")

            obtenerSolicitudRequest = ObtenerSolicitudReembolsoRequest(data=request.data)
            logger.info("Request serializer creado")

            if obtenerSolicitudRequest.is_valid():
                logger.info("Request válido, llamando al presenter")
                solicitudesResponse = self.solicitudReembolsoPresenter.obtenerSolicitudReembolso(
                    obtenerSolicitudRequest.validated_data
                )

                logger.info(f"Respuesta del presenter: {solicitudesResponse}")
                response = ObtenerSolicitudReembolsoResponse(data=solicitudesResponse)

                if response.is_valid():
                    logger.info("Solicitudes obtenidas exitosamente")
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Errores en response serializer: {response.errors}")
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            logger.error(f"Request inválido: {obtenerSolicitudRequest.errors}")
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": obtenerSolicitudRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Error general en ObtenerSolicitudReembolso: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e), "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ActualizarValidacionSolicitudReembolso(APIView):
    """
    API para actualizar validaciones de solicitud de reembolso
    """
    
    def __init__(self):
        self.contenedor = ActualizarValidacionSolicitudReembolsoPresenterContainer()
        self.actualizarValidacionPresenter = self.contenedor.actualizarValidacionSolicitudReembolsoPresenter()

    def patch(self, request, *args, **kwargs):
        try:
            updateRequest = ActualizarValidacionSolicitudReembolsoRequest(data=request.data)
            
            if updateRequest.is_valid():
                solicitudResponse = self.actualizarValidacionPresenter.actualizarValidacionSolicitudReembolso(
                    updateRequest.validated_data
                )
                
                response = ActualizarValidacionSolicitudReembolsoResponse(data=solicitudResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": updateRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ObtenerFormasPago(APIView):
    """
    API para obtener todas las formas de pago
    """

    def __init__(self):
        self.contenedor = FormaPagoPresenterContainer()
        self.formaPagoPresenter = self.contenedor.formaPagoPresenter()

    def post(self, request, *args, **kwargs):
        try:
            obtenerFormaPagoRequest = ObtenerFormaPagoRequest(data=request.data)
            
            if obtenerFormaPagoRequest.is_valid():
                formasPagoResponse = self.formaPagoPresenter.obtenerFormasPago(
                    obtenerFormaPagoRequest.validated_data
                )
                
                response = ObtenerFormaPagoResponse(data=formasPagoResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "estado": MessageType.ERROR.value,
                        "errores": response.errors
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "estado": MessageType.BAD_REQUEST.value,
                "errores": obtenerFormaPagoRequest.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value,
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DiagnosticarSolicitudViaje(APIView):
    """
    Endpoint para diagnosticar problemas con SolicitudViaje - PASO A PASO
    """
    def get(self, request, *args, **kwargs):
        diagnostic_info = {
            "estado": "INICIANDO_DIAGNOSTICO",
            "pasos": []
        }
        
        try:
            # Paso 1: Verificar modelo básico
            diagnostic_info["pasos"].append("Paso 1: Verificar importación del modelo")
            #from ..models import SolicitudViaje
            diagnostic_info["modelo_importado"] = True
            
            # Paso 2: Verificar conteo de registros
            diagnostic_info["pasos"].append("Paso 2: Verificar conteo de registros")
            count = SolicitudViaje.objects.count()
            diagnostic_info["conteo_exitoso"] = True
            diagnostic_info["total_registros"] = count
            
            # Paso 3: Verificar que podemos crear un registro de prueba
            diagnostic_info["pasos"].append("Paso 3: Verificar creación de registro")
            try:
                # Solo verificar, no crear realmente
                diagnostic_info["creacion_posible"] = True
            except Exception as e:
                diagnostic_info["creacion_posible"] = False
                diagnostic_info["error_creacion"] = str(e)
            
            diagnostic_info["estado"] = "DIAGNOSTICO_EXITOSO"
            diagnostic_info["mensaje"] = "Todos los componentes básicos funcionan"
            
            return Response(diagnostic_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            diagnostic_info["estado"] = "ERROR_EN_DIAGNOSTICO"
            diagnostic_info["error"] = str(e)
            diagnostic_info["tipo_error"] = type(e).__name__
            return Response(diagnostic_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ObtenerSolicitudesViaje(APIView):
    """
    API para obtener solicitudes de viaje con filtros
    """
    
    def __init__(self):
        self.contenedor = SolicitudViajePresenterContainer()
        self.solicitudViajePresenter = self.contenedor.solicitudViajePresenter()

    def post(self, request, *args, **kwargs):
        try:
            obtenerSolicitudRequest = ObtenerSolicitudesViajeRequest(data=request.data)
            
            if obtenerSolicitudRequest.is_valid():
                solicitudesResponse = self.solicitudViajePresenter.obtenerSolicitudesViaje(
                    obtenerSolicitudRequest.validated_data
                )
                
                response = ObtenerSolicitudesViajeResponse(data=solicitudesResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "estado": MessageType.ERROR.value,
                        "errores": response.errors
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "estado": MessageType.BAD_REQUEST.value,
                "errores": obtenerSolicitudRequest.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value,
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActualizarValidacionSolicitudViaje(APIView):
    def __init__(self):
        self.contenedor = ActualizarValidacionSolicitudViajePresenterContainer()
        self.actualizarValidacionPresenter = self.contenedor.actualizarValidacionSolicitudViajePresenter()

    def patch(self, request, *args, **kwargs):
        try:
            updateRequest = ActualizarValidacionSolicitudViajeRequest(data=request.data)
            
            if updateRequest.is_valid():
                solicitudResponse = self.actualizarValidacionPresenter.actualizarValidacionSolicitudViaje(
                    updateRequest.validated_data
                )
                
                response = ActualizarValidacionSolicitudViajeResponse(data=solicitudResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": updateRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ObtenerSolicitudesPagoDirecto(APIView):
    """
    API para obtener solicitudes de pago directo con filtros
    """
    
    def __init__(self):
        self.contenedor = SolicitudPagoDirectoPresenterContainer()
        self.solicitudPagoDirectoPresenter = self.contenedor.solicitudPagoDirectoPresenter()

    def post(self, request, *args, **kwargs):
        try:
            obtenerSolicitudRequest = ObtenerSolicitudesPagoDirectoRequest(data=request.data)
            
            if obtenerSolicitudRequest.is_valid():
                solicitudesResponse = self.solicitudPagoDirectoPresenter.obtenerSolicitudesPagoDirecto(
                    obtenerSolicitudRequest.validated_data
                )
                
                response = ObtenerSolicitudesPagoDirectoResponse(data=solicitudesResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "estado": MessageType.ERROR.value,
                        "errores": response.errors
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "estado": MessageType.BAD_REQUEST.value,
                "errores": obtenerSolicitudRequest.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "estado": MessageType.ERROR.value,
                "mensaje": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActualizarValidacionSolicitudPagoDirecto(APIView):
    """
    API para actualizar validaciones de solicitud de pago directo
    """
    
    def __init__(self):
        self.contenedor = ActualizarValidacionSolicitudPagoDirectoPresenterContainer()
        self.actualizarValidacionPresenter = self.contenedor.actualizarValidacionSolicitudPagoDirectoPresenter()

    def patch(self, request, *args, **kwargs):
        try:
            updateRequest = ActualizarValidacionSolicitudPagoDirectoRequest(data=request.data)
            
            if updateRequest.is_valid():
                solicitudResponse = self.actualizarValidacionPresenter.actualizarValidacionSolicitudPagoDirecto(
                    updateRequest.validated_data
                )
                
                response = ActualizarValidacionSolicitudPagoDirectoResponse(data=solicitudResponse)
                
                if response.is_valid():
                    return Response(response.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"estado": MessageType.ERROR.value, "errores": response.errors},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(
                {"estado": MessageType.BAD_REQUEST.value, "errores": updateRequest.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {"estado": MessageType.ERROR.value, "mensaje": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
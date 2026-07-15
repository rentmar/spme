#spme/spme_validaciones/views/solicitudes_fondos_usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

#Service
from ..services.solicitudes_fondos_usuario_service import SolicitudesFondosUsuarioService

#Serializer
from ..serializers.solicitudes_fondos_usuario_serializers import (
    SolicitudesFondosUsuarioResponseSerializer
)

logger = logging.getLogger(__name__)

class SolicitudesFondosUsuarioView(APIView):
    """
    Endpoint especializado para obtener solicitudes de fondos del usuario.
    
    GET /api/validaciones/solicitudes-fondos/
    
    Headers requeridos:
        Authorization: Bearer <token>
    
    Respuesta exitosa (200):
        {
            "tipo": "solicitudes_fondos",
            "total": 3,
            "solicitudes": [...],
            "resumen": {...}
        }
    
    Características:
    1. Funciona independientemente
    2. Diseñado para ser reutilizado por un endpoint maestro
    3. Incluye método as_service() para consumo interno
    
    Errores:
        401: Usuario no autenticado
        500: Error interno del servidor
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, service=None, **kwargs):
        """
         Constructor que permite inyección del servicio para testing.
        
        Args:
            service: Instancia del servicio (opcional, para tests)

        """
        super().__init__(**kwargs)
        self.service = service or SolicitudesFondosUsuarioService()
    
    def get(self, request):
        """
        Maneja peticiones GET para obtener solicitudes de fondos del usuario.
        
        Flujo:
        1. Extrae el ID del usuario del token JWT
        2. Delega la lógica de negocio al servicio especializado
        3. Valida y serializa la respuesta
        4. Retorna JSON estructurado
        
        Args:
            request: Objeto HttpRequest con datos del usuario autenticado
            
        Returns:
            Response con datos estructurados o error
        """
        try:
            #PASO 1, obtener id del usuario autenticado
            usuario_id = request.user.id

            logger.info(
                f"Obteniendo solicitudes de fondos para usuario ID={usuario_id}"
            )

            #Paso 2. Obtener datos del servicio
            resultado = self.service.obtener_solicitudes_usuario(usuario_id)

            # Paso 3: Validar y serializar respuesta
            serializer = SolicitudesFondosUsuarioResponseSerializer(data=resultado)

            if not serializer.is_valid():
                logger.error(
                    f"Error de serialización: {serializer.errors}"
                )
                return Response(
                    {
                        'error': 'Error al procesar los datos',
                        'detalle': serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Paso 4: Retornar respuesta exitosa
            logger.info(
                f"Solicitudes encontradas: {resultado['total']} "
                f"(Redactor: {resultado['resumen']['comoRedactor']}, "
                f"Revisor: {resultado['resumen']['comoRevisor']}, "
                f"Redactor-Revisor: {resultado['resumen']['comoRedactorRevisor']})"
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception(
                f"Error inesperado al obtener solicitudes: {str(e)}"
            )
            return Response(
                {
                    'error': 'Error al obtener solicitudes de fondos',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @classmethod
    def as_service(cls, usuario_id: int) -> dict:
        """
        Método de clase para usar el endpoint como servicio interno.
        
        Permite que otros endpoints (como un endpoint maestro) consuman
        este endpoint directamente sin hacer peticiones HTTP.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con solicitudes de fondos
            
        Ejemplo de uso desde otro endpoint:
            fondos = SolicitudesFondosUsuarioView.as_service(usuario_id)
        """
        service = SolicitudesFondosUsuarioService()
        return service.obtener_solicitudes_usuario(usuario_id)


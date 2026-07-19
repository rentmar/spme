# spme/spme_email/views/notificacion_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import logging

#Serializer
from ..serializers.notificacion_formularios_serializers import NotificacionBaseSerializer
#Servicios
from ..services.notificacion_service import NotificacionService

logger = logging.getLogger(__name__)

class NotificacionSolicitudView(APIView):
    """
    Endpoint para enviar notificaciones de solicitudes.
    POST /api-mail/email/notificaciones/enviar/

    ┌──────────────────┬──────────────────────┬──────────────────────┐
    │ Acción           │ A quién notifica     │ Campo requerido      │
    ├──────────────────┼──────────────────────┼──────────────────────┤
    │ revision         │ A los revisores      │ revisores_ids        │
    │ aprobacion       │ Al redactor          │ redactor_id          │
    │ rechazo          │ Al redactor          │ redactor_id          │
    │ nueva_revision   │ A los revisores      │ revisores_ids        │
    └──────────────────┴──────────────────────┴──────────────────────┘
    POST /api/notificaciones/enviar/
    Authorization: Bearer <JWT>

    {
        "tipo_solicitud": "fondos",
        "solicitud_id": 42,
        "accion": "revision",
        "destinatarios_ids": [68, 71],
        "base_url": "https://spme.gob.bo"
    }
    """
    permission_classes =[IsAuthenticated]

    #Inicializa la clase
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Inicializar el serivio
    
    def post(self, request):

        serializer = NotificacionBaseSerializer(data=request.data)

        #Validar la informacion
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        data = serializer.validated_data
            
        try:
            print(data)
            service = NotificacionService()
            resultado = service.enviar(
                tipo=data['tipo_solicitud'],
                solicitud_id=data['solicitud_id'],
                accion=data['accion'],
                destinatarios_ids=data['destinatarios_ids'],
                base_url=data['base_url'],
            ) 
            return Response({'success': True, **resultado})     
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    
    




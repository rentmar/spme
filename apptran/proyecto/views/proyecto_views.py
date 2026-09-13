#spme/apptran/proyecto/views/proyecto_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..services.proyecto_service import ProyectoService
import logging

logger = logging.getLogger(__name__)


class ProyectoEstructuraCompletaView(APIView):
    """
    Endpoint para obtener la estructura jerárquica completa:
    Proyecto → Actividades → Tareas
    
    GET /api/proyectos/{id}/estructura/
    """
    # permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proyecto_service = ProyectoService()
    
    def get(self, request, proyecto_id):
        """
        Retorna la estructura completa del proyecto con actividades y tareas
        
        Args:
            request: Request HTTP
            proyecto_id (int): ID del proyecto
            
        Returns:
            Response: Respuesta HTTP con la estructura del proyecto
        """
        try:
            logger.info(f"Obteniendo estructura del proyecto {proyecto_id}")
            
            resultado = self.proyecto_service.obtener_estructura_proyecto(proyecto_id)
            
            logger.info(f"Estructura del proyecto {proyecto_id} obtenida exitosamente")
            
            return Response(
                resultado,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error al obtener estructura del proyecto {proyecto_id}: {str(e)}")
            
            return Response(
                {
                    'success': False,
                    'error': 'Error al obtener la estructura del proyecto',
                    'message': str(e)
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ProyectoActividadesInactivasView(APIView):
    """
    Endpoint para obtener solo las actividades INACTIVAS de un proyecto
    
    GET /api/proyectos/{id}/actividades-inactivas/
    """
    # permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proyecto_service = ProyectoService()
    
    def get(self, request, proyecto_id):
        """
        Retorna solo las actividades inactivas del proyecto con sus tareas
        """
        try:
            logger.info(f"Obteniendo actividades inactivas del proyecto {proyecto_id}")
            
            resultado = self.proyecto_service.obtener_actividades_inactivas(proyecto_id)
            
            logger.info(f"Actividades inactivas del proyecto {proyecto_id} obtenidas exitosamente")
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error al obtener actividades inactivas del proyecto {proyecto_id}: {str(e)}")
            
            return Response(
                {
                    'success': False,
                    'error': 'Error al obtener las actividades inactivas',
                    'message': str(e)
                },
                status=status.HTTP_404_NOT_FOUND
            )

class ProyectoResumenView(APIView):
    """
    Endpoint para obtener el resumen del proyecto.

    GET /api/proyecto-resumen/{id}/
    """
    # permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proyecto_service = ProyectoService()

    def get(self, request, proyecto_id):
        """
        Retorna el resumen del proyecto (datos esenciales + relaciones clave).

        Args:
            request: Request HTTP
            proyecto_id (int): ID del proyecto

        Returns:
            Response: Respuesta HTTP con el resumen del proyecto
        """
        try:
            logger.info(f"Obteniendo resumen del proyecto {proyecto_id}")

            resultado = self.proyecto_service.obtener_resumen(proyecto_id)

            logger.info(f"Resumen del proyecto {proyecto_id} obtenido exitosamente")

            return Response(
                resultado,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error al obtener resumen del proyecto {proyecto_id}: {str(e)}")

            return Response(
                {
                    'success': False,
                    'error': 'Error al obtener el resumen del proyecto',
                    'message': str(e)
                },
                status=status.HTTP_404_NOT_FOUND
            )
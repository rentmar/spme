# spme_presupuesto/views/arbol_pres_plan_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.arbol_pres_plan_service import ArbolPresPlanService
from ..serializers.arbol_pres_plan_serializer import NodoPresPlanSerializer

class ArbolPresPlanView(APIView):
    """
    Vista para obtener el árbol de presupuesto planificado - Nivel 1.
    
    Endpoint:
        GET /api/proyectos/{proyecto_id}/arbol-presupuesto-plan/
    
    Respuesta exitosa (200):
        {
            "tipo_nodo": "proyecto",
            "id": 48,
            "nivel": 0,
            "datos": { ... },
            "actividades": [ ... ],
            "metadata": { ... }
        }
    
    Respuesta error (404):
        { "error": "Proyecto no encontrado" }
    """
    
    def get(self, request, proyecto_id):
        """
        Obtiene el árbol de presupuesto planificado para un proyecto.
        
        Args:
            request: Request HTTP
            proyecto_id (int): ID del proyecto
            
        Returns:
            Response: Nodo proyecto en formato JSON
        """
        try:
            service = ArbolPresPlanService()
            arbol = service.construir_arbol(proyecto_id)
            
            if not arbol:
                return Response(
                    {'error': 'Proyecto no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = NodoPresPlanSerializer(data=arbol)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# spme_presupuesto/views/presupuesto_tree_view_v3.py

from django.http import JsonResponse
from django.views import View
from spme_presupuesto.services.presupuesto_tree_v3.orchestrator import PresupuestoOrchestratorV3


class PresupuestoTreeViewV3(View):
    """
    Endpoint V3 para el árbol de seguimiento presupuestario.
    
    GET /api-pres/v3/proyecto/arbol-presupuesto/
    
    Parámetros:
        nodo: Tipo de nodo inicial (default: 'proyecto')
        id: ID del nodo (requerido)
        depth: Profundidad (default: 'all')
        direction: Dirección (default: 'down')
    """
    
    def get(self, request):
        # Obtener parámetros
        nodo = request.GET.get('nodo', 'proyecto')
        id_str = request.GET.get('id')
        depth = request.GET.get('depth', 'all')
        direction = request.GET.get('direction', 'down')
        
        # Validar id
        if not id_str:
            return JsonResponse({
                'error': 'El parámetro "id" es requerido',
                'ejemplo': '/api-pres/v3/proyecto/arbol-presupuesto/?nodo=proyecto&id=46&depth=all&direction=down'
            }, status=400)
        
        try:
            id = int(id_str)
        except ValueError:
            return JsonResponse({
                'error': 'El parámetro "id" debe ser un número entero'
            }, status=400)
        
        # Convertir depth a entero si es numérico
        if depth.isdigit():
            depth = int(depth)
        
        # Validar direction
        if direction not in ['down', 'up', 'both']:
            return JsonResponse({
                'error': 'El parámetro "direction" debe ser: down, up o both'
            }, status=400)
        
        # Construir árbol
        try:
            orchestrator = PresupuestoOrchestratorV3()
            response = orchestrator.build_tree(nodo, id, depth, direction)
            return JsonResponse(response.to_dict(), status=200)
        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': f'Error interno: {str(e)}'
            }, status=500)
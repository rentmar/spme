# spme_presupuesto/views/presupuesto_tree_view_v3.py

from django.http import JsonResponse
from django.views import View
from spme_presupuesto.services.presupuesto_tree_v3.orchestrator import PresupuestoOrchestratorV3
from ..services.presupuesto_tree_v3.orchestrator import PresupuestoOrchestratorV3
from ..services.presupuesto_tree_v3.enums import (
    TipoNodo, 
    Direccion,
    Profundidad,
)


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
        #1. Obtener parámetros
        nodo = request.GET.get('nodo', TipoNodo.PROYECTO.value)
        id_str = request.GET.get('id')
        depth = request.GET.get('depth', Profundidad.ALL)
        direction = request.GET.get('direction', Direccion.DOWN.value)
        
        #2. Validar id
        if not id_str:
            return JsonResponse({
                'error': 'El parámetro "id" es requerido',
                'ejemplo': '/api-pres/v3/proyecto/arbol-presupuesto/?nodo=proyecto&id=55&depth=all&direction=down'
            }, status=400)
        
        try:
            nodo_id = int(id_str)
        except ValueError:
            return JsonResponse({
                'error': 'El parámetro "id" debe ser un número entero'
            }, status=400)
        
        #3. Convertir depth a entero si es numérico
        if isinstance(depth, str) and depth.isdigit():
            depth = int(depth)
        
        #4. Validar direction
        direcciones_validas = [d.value for d in Direccion]
        if direction not in direcciones_validas:
            return JsonResponse({
                'error': f'El parámetro "direction" debe ser uno de los siguientes: {", ".join(direcciones_validas)}'
            }, status=400)
        
        #5. Construir árbol
        
        try:
            orchestrator = PresupuestoOrchestratorV3()
            response = orchestrator.build_tree(
                nodo=nodo,
                id=nodo_id,
                depth=depth,
                direction=direction
            )
            return JsonResponse(response.to_dict(), status=200)
            
        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Error interno: {str(e)}'
            }, status=500)
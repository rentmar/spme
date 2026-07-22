from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..services.tree import tree_orchestrator, Direction


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def arbol_endpoint(request):
    """
    Endpoint para obtener la estructura de árbol jerárquico.
    
    Parámetros GET:
        - nodo: Tipo de nodo inicial (proyecto, objetivogeneral)
        - id: ID del nodo inicial
        - depth: Profundidad (self, 1, 2, ..., all) [default: all]
        - direction: Dirección (down, up, both) [default: down]
    
    Ejemplos:
        GET /api/repositorio/arbol/?nodo=proyecto&id=5&depth=self
        GET /api/repositorio/arbol/?nodo=proyecto&id=5&depth=all
        GET /api/repositorio/arbol/?nodo=objetivogeneral&id=10&direction=up
    """
    try:
        # Obtener y validar parámetros
        node_type = request.GET.get('nodo', 'proyecto')
        node_id = request.GET.get('id')
        depth = request.GET.get('depth', 'all')
        direction = request.GET.get('direction', Direction.DOWN)
        
        # Validaciones
        if not node_id:
            return Response(
                {
                    'error': 'El parámetro "id" es requerido',
                    'ejemplo': '/api/repositorio/arbol/?nodo=proyecto&id=1'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Intentar convertir ID a entero si es posible
        try:
            node_id = int(node_id)
        except (ValueError, TypeError):
            pass  # Mantener como string si no es numérico
        
        # Validar dirección
        if direction not in [Direction.DOWN, Direction.UP, Direction.BOTH]:
            return Response(
                {
                    'error': f'Dirección no válida: {direction}',
                    'valores_permitidos': [Direction.DOWN, Direction.UP, Direction.BOTH]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar profundidad
        if depth not in ['self', 'all']:
            try:
                int(depth)
            except (ValueError, TypeError):
                return Response(
                    {
                        'error': f'Profundidad no válida: {depth}',
                        'valores_permitidos': ['self', 'all', '1', '2', '3', ...]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Construir árbol
        tree_response = tree_orchestrator.build_tree(
            node_type=node_type,
            node_id=node_id,
            depth=depth,
            direction=direction
        )
        
        # Retornar respuesta
        return Response(
            tree_response.to_dict(),
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                'error': 'Error interno al construir el árbol',
                'detalle': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
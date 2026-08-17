import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from spme_repositorio.services.repo_tree import repo_tree_orchestrator
from spme_repositorio.serializers.repo_tree_serializers import RepoTreeRequestSerializer

logger = logging.getLogger(__name__)


class RepoTreeView(APIView):
    """
    Endpoint para consultar el árbol de repositorio.

    Query params:
        proyecto_id: int - ID del proyecto para árbol completo
        nodo_id: int - ID del nodo específico
        nodo_tipo: str - Tipo de nodo (requerido si nodo_id está presente)
        include_children: bool - Incluir descendientes del nodo
        include_parent: bool - Incluir el padre del nodo
    """

    def get(self, request, *args, **kwargs):
        # Validar query params
        serializer = RepoTreeRequestSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        proyecto_id = validated_data.get('proyecto_id')
        nodo_id = validated_data.get('nodo_id')
        nodo_tipo = validated_data.get('nodo_tipo')
        include_children = validated_data.get('include_children', False)
        include_parent = validated_data.get('include_parent', False)

        try:
            # Modo 1: Árbol completo
            if proyecto_id and not nodo_id:
                response = repo_tree_orchestrator.build_tree(proyecto_id)
                return Response(response.to_dict(), status=status.HTTP_200_OK)

            # Modo 2: Nodo individual
            if nodo_id and nodo_tipo and not include_children and not include_parent:
                nodo = repo_tree_orchestrator.build_node(nodo_id, nodo_tipo)
                if not nodo:
                    return Response(
                        {'error': 'Nodo no encontrado'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                return Response(
                    {'nodo': nodo.to_dict()},
                    status=status.HTTP_200_OK,
                )

            # Modo 3: Subárbol (nodo + hijos)
            if nodo_id and nodo_tipo and include_children and not include_parent:
                nodo = repo_tree_orchestrator.build_subtree(nodo_id, nodo_tipo)
                if not nodo:
                    return Response(
                        {'error': 'Nodo no encontrado'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                return Response(
                    {'nodo': nodo.to_dict()},
                    status=status.HTTP_200_OK,
                )

            # Modo 4: Nodo con padre
            if nodo_id and nodo_tipo and include_parent and not include_children:
                nodo = repo_tree_orchestrator.build_node_with_parent(nodo_id, nodo_tipo)
                if not nodo:
                    return Response(
                        {'error': 'Nodo no encontrado'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                return Response(
                    {'padre': nodo.to_dict()},
                    status=status.HTTP_200_OK,
                )

            # Modo 5: Nodo con padre y hermanos
            if nodo_id and nodo_tipo and include_parent and include_children:
                nodo = repo_tree_orchestrator.build_node_with_parent_and_siblings(
                    nodo_id, nodo_tipo
                )
                if not nodo:
                    return Response(
                        {'error': 'Nodo no encontrado'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                return Response(
                    {'padre': nodo.to_dict()},
                    status=status.HTTP_200_OK,
                )

            # Combinación no soportada
            return Response(
                {'error': 'Combinación de parámetros no válida'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error construyendo árbol de repositorio: {e}")
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
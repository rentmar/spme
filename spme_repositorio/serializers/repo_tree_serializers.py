# spme/spme_repositorio/serializers/repo_tree_serializers.py
from rest_framework import serializers

class RepoTreeRequestSerializer(serializers.Serializer):
    """
    Serializer para la solicitud del árbol de repositorio.
    """

    proyecto_id = serializers.IntegerField(required=False, allow_null=True)
    nodo_id = serializers.IntegerField(required=False, allow_null=True)
    nodo_tipo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    include_children = serializers.BooleanField(required=False, default=False)
    include_parent = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        proyecto_id = attrs.get('proyecto_id')
        nodo_id = attrs.get('nodo_id')
        nodo_tipo = attrs.get('nodo_tipo')

        # Debe proporcionar al menos uno de los dos
        if not proyecto_id and not nodo_id:
            raise serializers.ValidationError(
                "Debe proporcionar 'proyecto_id' o 'nodo_id'"
            )

        # Si proporciona nodo_id, debe proporcionar nodo_tipo
        if nodo_id and not nodo_tipo:
            raise serializers.ValidationError(
                "Si proporciona 'nodo_id', debe proporcionar 'nodo_tipo'"
            )

        # Validar que nodo_tipo esté registrado
        if nodo_tipo:
            from spme_repositorio.services.repo_tree import repo_tree_orchestrator
            if not repo_tree_orchestrator.registry.is_registered(nodo_tipo):
                raise serializers.ValidationError(
                    f"Tipo de nodo '{nodo_tipo}' no válido"
                )

        return attrs
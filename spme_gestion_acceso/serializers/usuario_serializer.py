# spme/spme_gestion_acceso/serializers/usuario_serializer.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario  # Ajustar según tu estructura

class UsuarioSolicitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre',
            'paterno',
            'materno',
            'correo',
            'ci',
            'cargo',
        ]

from rest_framework import serializers
from spme_autenticacion.models import Usuario


class UsuarioCrudSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = '__all__'

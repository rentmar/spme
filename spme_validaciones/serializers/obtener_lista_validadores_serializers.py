#serializers
from rest_framework import serializers
from spme_autenticacion.models import Usuario

class UsuarioValidacionSerializers(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.CharField(source='correo')
    rol = serializers.CharField(source='cargo')
    username = serializers.CharField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'email', 'rol', 'username']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.paterno} {obj.materno}".strip()
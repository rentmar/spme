"""
Serializers para usuarios
"""
from rest_framework import serializers
from spme_autenticacion.models import Usuario

class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar usuarios
    """
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'nombre_completo',
            'email',
            'cargo'
        ]
        read_only_fields = fields
    
    def get_nombre_completo(self, obj):
        """Obtiene el nombre completo del usuario"""
        return obj.get_full_name()
    
    def get_email(self, obj):
        """Genera un email basado en el username"""
        # Si tienes un campo email real en el modelo, cámbialo por obj.email
        # Por ahora generaremos uno basado en el username
        if hasattr(obj, 'email') and obj.email:
            return obj.email
        else:
            return f"{obj.username}@empresa.com"
            
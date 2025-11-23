from rest_framework import serializers
from spme_autenticacion.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'paterno', 'materno', 
            'nombre_completo', 'ci', 'cargo', 'banco', 'numero_cuenta',
            'tipo_cuenta', 'permisos', 'is_active', 'is_staff', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()
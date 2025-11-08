from rest_framework import serializers
from ..models import UserInstanciaGestora, PermisoProyectoEspecifico
from ..services.permission_service import PermissionService

class UserInstanciaGestoraSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    usuario_nombre_completo = serializers.SerializerMethodField()
    instancia_gestora_nombre = serializers.CharField(source='instancia_gestora.instancia', read_only=True)
    nivel_acceso_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInstanciaGestora
        fields = [
            'id', 'usuario', 'usuario_username', 'usuario_nombre_completo',
            'instancia_gestora', 'instancia_gestora_nombre', 'nivel_acceso', 
            'nivel_acceso_display', 'activo', 'fecha_asignacion'
        ]
        read_only_fields = ['fecha_asignacion']
    
    def get_usuario_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    
    def get_nivel_acceso_display(self, obj):
        return PermissionService().obtener_nombre_nivel_acceso(obj.nivel_acceso)

class PermisoProyectoEspecificoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    usuario_nombre_completo = serializers.SerializerMethodField()
    proyecto_codigo = serializers.CharField(source='proyecto.codigo', read_only=True)
    proyecto_titulo = serializers.CharField(source='proyecto.titulo', read_only=True)
    asignado_por_username = serializers.CharField(source='asignado_por.username', read_only=True)
    tipo_acceso_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PermisoProyectoEspecifico
        fields = [
            'id', 'usuario', 'usuario_username', 'usuario_nombre_completo',
            'proyecto', 'proyecto_codigo', 'proyecto_titulo', 'tipo_acceso', 
            'tipo_acceso_display', 'fecha_asignacion', 'fecha_expiracion', 
            'asignado_por', 'asignado_por_username', 'motivo', 'activo'
        ]
        read_only_fields = ['fecha_asignacion']
    
    def get_usuario_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    
    def get_tipo_acceso_display(self, obj):
        return PermissionService().obtener_nombre_nivel_acceso(obj.tipo_acceso)
    
    def validate(self, data):
        from django.utils import timezone
        
        if data.get('fecha_expiracion') and data['fecha_expiracion'] < timezone.now():
            raise serializers.ValidationError(
                "La fecha de expiración no puede ser en el pasado"
            )
        
        return data
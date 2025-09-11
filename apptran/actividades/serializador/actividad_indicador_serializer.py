# serializers.py
from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad, TipoActividad
from spme_autenticacion.models import Usuario


class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = '__all__'

class UsuarioBasicSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'paterno', 'materno', 'nombre_completo', 'ci', 'cargo']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()

class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):
    responsable_info = UsuarioBasicSerializer(source='responsable', read_only=True)
    tipo_info = TipoActividadSerializer(source='tipo', read_only=True)
    tareas = TareaActividadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Actividad
        fields = '__all__'
    
    def create(self, validated_data):
        # Generar código automático si no se proporciona
        if not validated_data.get('codigo'):
            from django.utils import timezone
            year = timezone.now().year
            count = Actividad.objects.filter(fecha_programada__year=year).count() + 1
            validated_data['codigo'] = f"ACT-{year}-{count:04d}"
        
        return super().create(validated_data)
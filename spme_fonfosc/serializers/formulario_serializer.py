from rest_framework import serializers
from spme_fonfosc.models.formulario import Formulario


class FormularioSerializer(serializers.ModelSerializer):
    creado_por_username = serializers.CharField(
        source='creado_por.username', 
        read_only=True
    )
    creado_por_nombre_completo = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_display', 
        read_only=True
    )
    
    class Meta:
        model = Formulario
        fields = [
            'id',
            'nombre',
            'titulo',
            'descripcion',
            'version',
            'estado',
            'estado_display',
            'definicion_json',
            'creado_por',
            'creado_por_username',
            'creado_por_nombre_completo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'creado_por', 
            'fecha_creacion', 
            'fecha_actualizacion',
            'estado_display'
        ]
    
    def get_creado_por_nombre_completo(self, obj):
        if obj.creado_por:
            return obj.creado_por.get_full_name()
        return None
    
    def validate_definicion_json(self, value):
        """Valida la estructura del JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("definicion_json debe ser un objeto JSON")
        
        if 'sections' not in value:
            raise serializers.ValidationError("definicion_json debe contener 'sections'")
        
        if not isinstance(value['sections'], list):
            raise serializers.ValidationError("'sections' debe ser una lista")
        
        return value
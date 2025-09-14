# serializers.py
from rest_framework import serializers
#from .models import Actividad, TareaActividad, Proyecto
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad

class TareaActividadReporteSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = TareaActividad
        fields = ['id', 'titulo', 'descripcion', 'estado', 'estado_display', 
                 'fecha_creacion', 'fecha_limite', 'presupuesto']

class ActividadReporteSerializer(serializers.ModelSerializer):
    tareas = TareaActividadReporteSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    proyecto_info = serializers.SerializerMethodField()
    responsable_info = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = '__all__'
    
    def get_proyecto_info(self, obj):
        if obj.proyecto:
            return {
                'id': obj.proyecto.id,
                'codigo': obj.proyecto.codigo,
                'titulo': obj.proyecto.titulo
            }
        return None
    
    def get_responsable_info(self, obj):
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'nombre': obj.responsable.get_full_name(),
                'username': obj.responsable.username
            }
        return None
    
    def get_tipo_display(self, obj):
        if obj.tipo:
            return f"{obj.tipo.sigla} - {obj.tipo.tipo_actividad}"
        return 'No definido'
# serializers.py
from rest_framework import serializers
from spme_actividades.models import Actividad


class ActividadGanntSerializer(serializers.ModelSerializer):
    nombre_responsable = serializers.SerializerMethodField()
    nombre_corto = serializers.CharField(source='nombreCorto')
    grado_ejecucion = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    descripcion = serializers.SerializerMethodField()
    fecha_programada = serializers.SerializerMethodField()
    fecha_inicio = serializers.SerializerMethodField()
    fecha_cierre = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = [
            'nombre_responsable', 'codigo', 'nombre_corto', 'descripcion',
            'tipo', 'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'grado_ejecucion', 'estado'
        ]
    
    def get_nombre_responsable(self, obj):
        if obj.responsable:
            nombre_completo = obj.responsable.get_full_name()
            return nombre_completo if nombre_completo else "Sin Responsable"
        return "Sin Responsable"
    
    def get_grado_ejecucion(self, obj):
        return obj.gradoEjecucion if obj.gradoEjecucion is not None else "Sin definir"
    
    def get_tipo(self, obj):
        if obj.tipo:
            return obj.tipo.tipo_actividad if obj.tipo.tipo_actividad else "Sin tipo"
        return "Sin tipo"
    
    def get_descripcion(self, obj):
        return obj.descripcion if obj.descripcion else "Sin descripción"
    
    def get_fecha_programada(self, obj):
        return obj.fecha_programada if obj.fecha_programada else "Sin fecha programada"
    
    def get_fecha_inicio(self, obj):
        return obj.fecha_inicio if obj.fecha_inicio else "Sin fecha de inicio"
    
    def get_fecha_cierre(self, obj):
        return obj.fecha_cierre if obj.fecha_cierre else "Sin fecha de cierre"
    
    def get_estado(self, obj):
        return obj.estado if obj.estado else "PLAN"
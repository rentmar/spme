# serializers.py
from rest_framework import serializers
#from .models import PlanificacionProyecto, CambioPlanificacion
from spme_planificacion.models import PlanificacionProyecto, CambioPlanificacion

class CambioPlanificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambioPlanificacion
        fields = [
            'id', 'tipo_cambio', 'datos_anteriores', 'datos_nuevos',
            'descripcion', 'realizado_por', 'realizado_el'
        ]

class PlanificacionProyectoSerializer(serializers.ModelSerializer):
    # Serializer method field para contar actividades
    total_actividades = serializers.SerializerMethodField()
    
    # Serializer method field para el presupuesto total
    presupuesto_total = serializers.SerializerMethodField()
    
    # Incluir cambios relacionados
    cambios = CambioPlanificacionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PlanificacionProyecto
        fields = [
            'id', 'proyecto', 'table_config', 'rows_data', 'version',
            'creado', 'actualizado', 'creado_por', 'total_actividades',
            'presupuesto_total', 'cambios', 'vigente',
        ]
        read_only_fields = ['id', 'creado', 'actualizado']
    
    def get_total_actividades(self, obj):
        """Obtener el total de actividades en rows_data"""
        if isinstance(obj.rows_data, list):
            return len(obj.rows_data)
        return 0
    
    def get_presupuesto_total(self, obj):
        """Calcular el presupuesto total de todas las actividades"""
        if isinstance(obj.rows_data, list):
            total = sum(
                float(actividad.get('presupuesto', 0)) 
                for actividad in obj.rows_data 
                if actividad.get('presupuesto')
            )
            return round(total, 2)
        return 0
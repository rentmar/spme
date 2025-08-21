# serializers.py
from rest_framework import serializers
from spme_planificacion.models import PlanificacionProyecto, CambioPlanificacion

class PlanificacionProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanificacionProyecto
        fields = '__all__'

class CambioPlanificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambioPlanificacion
        fields = '__all__'

class HistorialPlanificacionSerializer(serializers.ModelSerializer):
    cambios = CambioPlanificacionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PlanificacionProyecto
        fields = ['id', 'proyecto', 'version', 'creado', 'actualizado', 'creado_por', 'cambios']
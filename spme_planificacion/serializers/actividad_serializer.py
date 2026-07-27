# spme/spme_planificacion/serializers/actividad_serializer.py
from rest_framework import serializers
from spme_actividades.models import Actividad

class ActividadActualizarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    tipo_actividad_id = serializers.IntegerField(source='tipo_id', required=False)
    
    class Meta:
        model = Actividad
        fields = [
            'id',
            'nombreCorto',
            'descripcion',
            'estado',
            'tipo_actividad_id',
            'responsable_id',
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'presupuesto',
            'totalEjecutado',
            'procedencia_fondos',
            'supuestos',
            'riesgos',
            'objetivo_de_actividad',
            'gradoEjecucion',
            'factoresCriticos',
        ]
from rest_framework import serializers
from spme_actividades.models import Actividad, TipoActividad

class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = ['id', 'sigla', 'tipo_actividad']

class ActividadSerializer(serializers.ModelSerializer):
    responsable = serializers.StringRelatedField()
    proyecto = serializers.StringRelatedField()
    
    class Meta:
        model = Actividad
        fields = '__all__'

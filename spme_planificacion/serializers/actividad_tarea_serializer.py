from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad


class ActividadPlanificacionSerializador(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'


class TareaActividadPlanificacionSerializador(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'

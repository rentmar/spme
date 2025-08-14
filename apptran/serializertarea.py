from rest_framework import serializers
from spme_actividades.models import TareaActividad


class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'

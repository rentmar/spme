from rest_framework import serializers
from spme_actividades.models import TareaActividad


class TareaActividadSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    
    class Meta:
        model = TareaActividad
        fields = '__all__'

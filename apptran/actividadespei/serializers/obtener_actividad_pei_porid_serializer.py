# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei


class TareaActividadPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividadPei
        fields = '__all__'

class ActividadConTareasSerializer(serializers.ModelSerializer):
    # Campo para las tareas relacionadas
    tareas_pei = TareaActividadPeiSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActividadPei
        fields = '__all__'
# serializers.py
from rest_framework import serializers
from ..models import CambioPlanificacion
#from .models import CambioPlanificacion

class CambioPlanificacionSerializer(serializers.ModelSerializer):
    realizado_el = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = CambioPlanificacion
        fields = [
            'id',
            'tipo_cambio',
            'datos_anteriores',
            'datos_nuevos',
            'descripcion',
            'realizado_por',
            'realizado_el',
            'planificacion'
        ]
        read_only_fields = ['id', 'realizado_el']
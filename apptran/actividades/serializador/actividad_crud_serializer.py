#Serializador para crud de actividades
from rest_framework import serializers
from spme_actividades.models import Actividad 

class ActividadCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'
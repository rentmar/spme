from rest_framework import serializers
from ..models import CambioPlanificacion


class CambioPlanificacionProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CambioPlanificacion
        fields = "__all__"

# class PlanificacionProyectoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PlanificacionProyecto
#         fields = '__all__'

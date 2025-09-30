from rest_framework import serializers
from ..models import PlanificacionProyecto

class PlanificacionProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanificacionProyecto
        fields = '__all__'



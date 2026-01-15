from rest_framework import serializers
from ..models import PlanificacionPei

class PlanificacionPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanificacionPei
        fields = '__all__'
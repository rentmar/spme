from rest_framework import serializers
from spme_estructuracion_pei.models import *
from spme_monitoreo.models import InfActividad

class InformeActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfActividad
        fields = '__all__'
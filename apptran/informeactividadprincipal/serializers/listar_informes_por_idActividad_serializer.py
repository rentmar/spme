#Serializador
from rest_framework import serializers
from spme_monitoreo.models import InformeActividadPrincipal

class InformeActividadPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeActividadPrincipal
        fields = '__all__'
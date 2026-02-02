
from rest_framework import serializers
from spme_monitoreo.models import InformeActividadPrincipal

class InformeActividadCrudSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    
    class Meta:
        model = InformeActividadPrincipal
        fields = '__all__'

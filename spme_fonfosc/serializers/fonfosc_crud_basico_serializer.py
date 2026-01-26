from rest_framework import serializers
from spme_monitoreo.models import SolicitudFondosActPei
from ..models import ProyectoFonFosc

class ProyectoFonFoscSerializer(serializers.ModelSerializer):
    #codigo = serializers.CharField(read_only=True)
    class Meta:
        model = ProyectoFonFosc
        fields = '__all__'
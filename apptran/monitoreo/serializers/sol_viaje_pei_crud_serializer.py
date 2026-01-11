from rest_framework import serializers
from spme_monitoreo.models import SolicitudViajeActPei

class SolicitudViajeActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudViajeActPei
        fields = '__all__'
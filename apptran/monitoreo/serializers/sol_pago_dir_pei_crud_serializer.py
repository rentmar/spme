from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirectoActPei


class SolicitudPagoDirectoActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirectoActPei
        fields = '__all__'
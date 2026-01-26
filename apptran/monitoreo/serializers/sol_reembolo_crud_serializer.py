from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolso

class SolicitudReembolsoV2Serializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReembolso
        fields = '__all__'
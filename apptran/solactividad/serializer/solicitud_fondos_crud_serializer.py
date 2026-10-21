# spme/apptran/solactividad/serializer/solicitud_fondos_crud_serializer.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudFondos

class SolicitudFondosCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = '__all__'
from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentasActPei

class RendicionCuentasActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentasActPei
        fields = '__all__'
#Serializador
from rest_framework import serializers
from spme_monitoreo.models import InformeTareaPrincipal

class InformeTareaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeTareaPrincipal
        fields = '__all__'
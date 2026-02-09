from rest_framework import serializers
from ..models import BitacoraIndicadorROG 

class BitacoraIndicadorROGSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicadorROG
        fields = '__all__'
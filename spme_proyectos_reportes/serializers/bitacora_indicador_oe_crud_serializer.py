from rest_framework import serializers
from ..models import BitacoraIndicadorOE

class BitacoraIndicadorOESerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicadorOE
        fields = '__all__'
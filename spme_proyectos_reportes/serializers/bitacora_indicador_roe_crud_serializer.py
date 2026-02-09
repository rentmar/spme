from rest_framework import serializers
from ..models import BitacoraIndicadorROE

class BitacoraIndicadorROESerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicadorROE
        fields = '__all__'
from rest_framework import serializers
from ..models import (
    BitacoraIndicadorOG,
    )

class BitacoraIndicadorOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicadorOG
        fields = '__all__'


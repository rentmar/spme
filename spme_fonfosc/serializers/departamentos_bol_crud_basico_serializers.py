from rest_framework import serializers
from ..models import DepartamentoBolivia

class DepBoliviaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartamentoBolivia
        fields = '__all__'
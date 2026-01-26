from rest_framework import serializers
from ..models import Institucion

class InstitucionSerializer(serializers.ModelSerializer):
    #codigo = serializers.CharField(read_only=True)
    class Meta:
        model = Institucion
        fields = '__all__'
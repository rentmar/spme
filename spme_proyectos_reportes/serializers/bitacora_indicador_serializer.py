from rest_framework import serializers
from spme_proyectos_reportes.models import BitacoraIndicador


#Serializador Model PEI
class BitacoraIndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicador
        fields = '__all__'

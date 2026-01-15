from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei

#Serializador Model PEI
class ActividadPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadPei
        fields = '__all__'
 
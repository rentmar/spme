from rest_framework import serializers
from spme_estructuracion_pei.models import TareaActividadPei

class TareaActividadPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividadPei
        fields = '__all__'
     

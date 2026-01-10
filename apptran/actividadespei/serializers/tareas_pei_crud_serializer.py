from rest_framework import serializers
from spme_estructuracion_pei.models import TareaActividadPei


class TareaPeiActividadPeiSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    
    class Meta:
        model = TareaActividadPei
        fields = '__all__'

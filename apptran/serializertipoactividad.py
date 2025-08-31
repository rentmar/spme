from rest_framework import serializers
from spme_actividades.models import TipoActividad

class TipoActividadSer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = '__all__'
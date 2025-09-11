from rest_framework import serializers
from spme_monitoreo.models import InformeActividad

#Serializador Model: DiagramaEstructura
class InformeActividadSer(serializers.ModelSerializer):
    class Meta:
        model = InformeActividad
        fields = '__all__'

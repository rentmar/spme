# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import InfTarea, TareaActividad

class InfTareaMinimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfTarea
        fields = '__all__'



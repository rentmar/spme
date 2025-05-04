from rest_framework import serializers
from spme_web.models import Tarea


#Serializador del modelo
class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'
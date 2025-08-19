from rest_framework import serializers
from spme_estructuracion_proyecto.models import EfectoProyecto

class EfectoProyectoSer(serializers.ModelSerializer):
    class Meta:
        model = EfectoProyecto
        fields = '__all__'
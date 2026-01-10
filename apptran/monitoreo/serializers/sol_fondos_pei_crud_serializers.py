from rest_framework import serializers
from spme_monitoreo.models import SolicitudFondosActPei
#from spme_actividades.models import TareaActividad

class SolicitudFondosPeiSerializer(serializers.ModelSerializer):
    #codigo = serializers.CharField(read_only=True)
    class Meta:
        model = SolicitudFondosActPei
        fields = '__all__'
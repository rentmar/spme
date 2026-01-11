from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolsoActPei
#from spme_monitoreo.models import SolicitudFondosActPei

class SolicitudReembolsoActPeiSerializer(serializers.ModelSerializer):
    #codigo = serializers.CharField(read_only=True)
    class Meta:
        model = SolicitudReembolsoActPei
        fields = '__all__'
        

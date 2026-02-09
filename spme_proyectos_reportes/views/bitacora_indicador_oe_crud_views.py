from rest_framework import viewsets
from ..models import BitacoraIndicadorOE
from ..serializers.bitacora_indicador_oe_crud_serializer import BitacoraIndicadorOESerializer

class BitacoraIndicadorOEViewset(viewsets.ModelViewSet):
    queryset = BitacoraIndicadorOE.objects.all()
    serializer_class = BitacoraIndicadorOESerializer
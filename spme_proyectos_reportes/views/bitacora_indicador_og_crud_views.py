from rest_framework import viewsets        
from ..models import BitacoraIndicadorOG
from ..serializers.bitacora_indicador_og_crud_serializer import BitacoraIndicadorOGSerializer

class BitacoraIndicadorOGViewset(viewsets.ModelViewSet):
    queryset = BitacoraIndicadorOG.objects.all()
    serializer_class = BitacoraIndicadorOGSerializer

    
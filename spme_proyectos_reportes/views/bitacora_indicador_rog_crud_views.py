from rest_framework import viewsets
from ..models import BitacoraIndicadorROG
from ..serializers.bitacora_indicador_rog_crud_serializer import BitacoraIndicadorROGSerializer

class BitacoraIndicadorROGViewset(viewsets.ModelViewSet):
    queryset = BitacoraIndicadorROG.objects.all()
    serializer_class = BitacoraIndicadorROGSerializer
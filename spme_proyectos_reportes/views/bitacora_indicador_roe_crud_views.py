from rest_framework import viewsets
from ..models import BitacoraIndicadorROE
from ..serializers.bitacora_indicador_roe_crud_serializer import BitacoraIndicadorROESerializer

class BitacoraIndicadorROEViewset(viewsets.ModelViewSet):
    queryset = BitacoraIndicadorROE.objects.all()
    serializer_class = BitacoraIndicadorROESerializer
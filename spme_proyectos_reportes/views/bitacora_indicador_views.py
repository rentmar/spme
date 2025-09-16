from rest_framework import viewsets
from ..serializers.bitacora_indicador_serializer import BitacoraIndicadorSerializer
from spme_proyectos_reportes.models import BitacoraIndicador


class BitacoraIndicadorViews(viewsets.ModelViewSet):
    queryset = BitacoraIndicador.objects.all()
    serializer_class = BitacoraIndicadorSerializer
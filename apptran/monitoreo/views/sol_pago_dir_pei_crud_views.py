from rest_framework import viewsets
from spme_monitoreo.models import SolicitudPagoDirectoActPei
from ..serializers.sol_pago_dir_pei_crud_serializer import SolicitudPagoDirectoActPeiSerializer

class SolicitudPagoDirectoActPeiView(viewsets.ModelViewSet):
    queryset = SolicitudPagoDirectoActPei.objects.all()
    serializer_class = SolicitudPagoDirectoActPeiSerializer

from rest_framework import viewsets
from spme_monitoreo.models import SolicitudReembolso
from ..serializers.sol_reembolo_crud_serializer import SolicitudReembolsoV2Serializer

class SolicitudReembolsoV2View(viewsets.ModelViewSet):
    queryset = SolicitudReembolso.objects.all()
    serializer_class = SolicitudReembolsoV2Serializer
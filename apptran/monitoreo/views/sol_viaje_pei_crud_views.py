from rest_framework import viewsets
from spme_monitoreo.models import SolicitudViajeActPei
from ..serializers.sol_viaje_pei_crud_serializer import SolicitudViajeActPeiSerializer

class SolicitudViajeActPeiView(viewsets.ModelViewSet):
    queryset = SolicitudViajeActPei.objects.all()
    serializer_class = SolicitudViajeActPeiSerializer
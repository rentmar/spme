from rest_framework import viewsets
from spme_monitoreo.models import SolicitudReembolsoActPei
from ..serializers.sol_reembolso_pei_crud_serializer import SolicitudReembolsoActPeiSerializer
# from spme_monitoreo.models import SolicitudFondosActPei
# from ..serializers.sol_fondos_pei_crud_serializers import SolicitudFondosPeiSerializer

class SolicitudReembolsoActPeiView(viewsets.ModelViewSet):
    queryset = SolicitudReembolsoActPei.objects.all()
    serializer_class = SolicitudReembolsoActPeiSerializer

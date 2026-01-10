from rest_framework import viewsets
from spme_monitoreo.models import SolicitudFondosActPei
from ..serializers.sol_fondos_pei_crud_serializers import SolicitudFondosPeiSerializer
#from spme_actividades.models import TareaActividad
#from .serializertarea import TareaActividadSerializer

class SolicitudFondosPeiView(viewsets.ModelViewSet):
    queryset = SolicitudFondosActPei.objects.all()
    serializer_class = SolicitudFondosPeiSerializer



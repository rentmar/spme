from rest_framework import viewsets
from spme_monitoreo.models import InformeActividadPrincipal
from ..serializers.informe_actividad_principal_serializer import InformeActividadPrincipalSerializer

class InformeActividadPrincipalView(viewsets.ModelViewSet):
    queryset = InformeActividadPrincipal.objects.all()
    serializer_class = InformeActividadPrincipalSerializer
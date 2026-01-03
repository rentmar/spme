from rest_framework import viewsets
from spme_monitoreo.models import InformeTareaPrincipal
from ..serializers.informe_tarea_principal_serializer import InformeTareaPrincipalSerializer

class InformeTareaPrincipalView(viewsets.ModelViewSet):
    queryset = InformeTareaPrincipal.objects.all()
    serializer_class = InformeTareaPrincipalSerializer
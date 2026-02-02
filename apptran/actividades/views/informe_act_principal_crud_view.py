from rest_framework import viewsets
from spme_monitoreo.models import InformeActividadPrincipal
from ..serializador.informe_act_principal_crud_serializer import InformeActividadCrudSerializer


class InformeActividadPrincipalCrudView(viewsets.ModelViewSet):
    queryset = InformeActividadPrincipal.objects.all()
    serializer_class = InformeActividadCrudSerializer


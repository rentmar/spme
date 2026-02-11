from rest_framework import viewsets
from spme_monitoreo.models import SolicitudFondos
from ..serializer.solicitud_fondos_crud_serializer import SolicitudFondosCrudSerializer


class SolicitudFondosCrudViews(viewsets.ModelViewSet):
    queryset = SolicitudFondos.objects.all()
    serializer_class = SolicitudFondosCrudSerializer

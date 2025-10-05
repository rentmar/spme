from rest_framework import viewsets
from spme_monitoreo.models import InfActividad
from ..serializers.informe_actividad_serializer import InformeActividadSerializer


class InformeActividadVersionMView(viewsets.ModelViewSet):
    queryset = InfActividad.objects.all()
    serializer_class = InformeActividadSerializer
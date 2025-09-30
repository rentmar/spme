from rest_framework import viewsets
from spme_planificacion.models import CambioPlanificacion
from ..serializers.cambio_planificacion_proyecto_serializer import CambioPlanificacionProyectoSerializer


class CambioPlanificacionProyectoViewSet(viewsets.ModelViewSet):
    queryset = CambioPlanificacion.objects.all()
    serializer_class = CambioPlanificacionProyectoSerializer



from rest_framework import viewsets
from spme_planificacion.models import PlanificacionProyecto
from ..serializers.planificacion_proyecto_serializer import PlanificacionProyectoSerializer

class PlanificacionProyectoViewSet(viewsets.ModelViewSet):
    queryset = PlanificacionProyecto.objects.all()
    serializer_class = PlanificacionProyectoSerializer






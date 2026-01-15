from rest_framework import viewsets
from spme_planificacion.models import PlanificacionPei
from ..serializers.planificacion_pei_crud_serializers import PlanificacionPeiSerializer

class PlanificacionPeiViewSet(viewsets.ModelViewSet):
    queryset = PlanificacionPei.objects.all()
    serializer_class = PlanificacionPeiSerializer

from rest_framework import viewsets
from spme_estructuracion_pei.models import TareaActividadPei
from ..serializers.tareas_actividad_pei_serializer import TareaActividadPeiSerializer


class TareaActividadPeiViewSet(viewsets.ModelViewSet):
    queryset = TareaActividadPei.objects.all()
    serializer_class = TareaActividadPeiSerializer
    
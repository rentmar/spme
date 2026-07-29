from rest_framework import viewsets
from spme_actividades.models import Actividad, TareaActividad
from ..serializers.actividad_tarea_serializer import ActividadPlanificacionSerializador, TareaActividadPlanificacionSerializador

class ActividadPlanificacionViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadPlanificacionSerializador

class TareaPlanificacionViewSet(viewsets.ModelViewSet):
    queryset = TareaActividad.objects.all()
    serializer_class = TareaActividadPlanificacionSerializador







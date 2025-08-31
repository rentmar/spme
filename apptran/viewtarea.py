from rest_framework import viewsets
from spme_actividades.models import TareaActividad
from .serializertarea import TareaActividadSerializer

class TareaActividadView(viewsets.ModelViewSet):
    queryset = TareaActividad.objects.all()
    serializer_class = TareaActividadSerializer


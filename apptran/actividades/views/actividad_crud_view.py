from rest_framework import viewsets
from spme_actividades.models import TareaActividad, Actividad
from ..serializador.actividad_crud_serializer import ActividadCrudSerializer

class ActividadCrudView(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadCrudSerializer
from rest_framework import viewsets
from spme_actividades.models import TipoActividad
from .serializertipoactividad import TipoActividadSer

class TipoActividadView(viewsets.ModelViewSet):
    queryset = TipoActividad.objects.all()
    serializer_class = TipoActividadSer
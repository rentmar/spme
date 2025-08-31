from rest_framework import viewsets
from spme_estructuracion_proyecto.models import EfectoProyecto
from .serializerefecto import EfectoProyectoSer


class EfectoProyectoView(viewsets.ModelViewSet):
    queryset = EfectoProyecto.objects.all()
    serializer_class = EfectoProyectoSer
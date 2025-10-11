from rest_framework import viewsets
from spme_monitoreo.models import InfTarea
from ..serializers.informe_tarea_serializer import InfTareaMinimoSerializer

class InfTareaMinViews(viewsets.ModelViewSet):
    queryset = InfTarea.objects.all()
    serializer_class = InfTareaMinimoSerializer



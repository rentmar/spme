from rest_framework import viewsets
from spme_fonfosc.models import ProyectoFonFosc
from ..serializers.fonfosc_crud_basico_serializer import ProyectoFonFoscSerializer
#from spme_actividades.models import TareaActividad
#from .serializertarea import TareaActividadSerializer

class ProyectoFonFoscViews(viewsets.ModelViewSet):
    queryset = ProyectoFonFosc.objects.all()
    serializer_class = ProyectoFonFoscSerializer
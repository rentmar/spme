from rest_framework import viewsets
from spme_fonfosc.models import Institucion
from ..serializers.fonfosc_crud_basico_serializer import ProyectoFonFoscSerializer
from ..serializers.institucion_crud_basico_serializer import InstitucionSerializer
#from spme_actividades.models import TareaActividad
#from .serializertarea import TareaActividadSerializer

class InstitucionViews(viewsets.ModelViewSet):
    queryset = Institucion.objects.all()
    serializer_class = InstitucionSerializer
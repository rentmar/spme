from rest_framework import viewsets
from spme_estructuracion_pei.models import TareaActividadPei
from ..serializers.tareas_pei_crud_serializer import TareaPeiActividadPeiSerializer
#from spme_actividades.models import TareaActividad
#from .serializertarea import TareaActividadSerializer

class TareaPeiActividadPeiView(viewsets.ModelViewSet):
    queryset = TareaActividadPei.objects.all()
    serializer_class = TareaPeiActividadPeiSerializer


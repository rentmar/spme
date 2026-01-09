from rest_framework import viewsets
from ..serializers.actividad_pei_serializer import ActividadPeiSerializer
from spme_estructuracion_pei.models import ActividadPei

class ActividadPeiViewModel(viewsets.ModelViewSet):
    queryset = ActividadPei.objects.all()
    serializer_class = ActividadPeiSerializer

    
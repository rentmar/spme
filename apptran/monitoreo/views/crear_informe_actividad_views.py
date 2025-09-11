from rest_framework import viewsets
from ..serializers.crear_informe_actividad_serializer import InformeActividadSer
from spme_monitoreo.models import InformeActividad

#Endpoitn tipo MODEL: Pei
class InformeActividadView(viewsets.ModelViewSet):
    queryset = InformeActividad.objects.all()
    serializer_class = InformeActividadSer
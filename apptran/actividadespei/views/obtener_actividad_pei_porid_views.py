# views.py
from rest_framework import generics
from rest_framework.response import Response
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei
from ..serializers.obtener_actividad_pei_porid_serializer import ActividadConTareasSerializer

class ActividadConTareasView(generics.RetrieveAPIView):
    """
    Endpoint para obtener una actividad por su ID con todas sus tareas.
    GET /api/actividades/{id}/con-tareas/
    """
    queryset = ActividadPei.objects.all()
    serializer_class = ActividadConTareasSerializer
    lookup_field = 'id'
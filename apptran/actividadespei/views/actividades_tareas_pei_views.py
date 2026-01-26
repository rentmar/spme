from rest_framework import generics
from rest_framework.response import Response
from spme_estructuracion_pei.models import ActividadPei
from ..serializers.actividades_tareas_pei_serializer import TareaActividadPei, ActividadPeiSerializer


class ActividadPeiConTareasListView(generics.ListAPIView):
    """
    EndPoint que retorna todas las actividades con sus tareas relacionadas
    """
    queryset = ActividadPei.objects.all().prefetch_related('tareas_pei')
    serializer_class = ActividadPeiSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Formatear la respuesta según el formato solicitado
        data = []
        for actividad_data in serializer.data:
            actividad_formateada = {
                'id': actividad_data['id'],
                'codigo': actividad_data['codigo'],
                'nombreCorto': actividad_data['nombreCorto'],
                'descripcion': actividad_data['descripcion'],
                'estado': actividad_data['estado'],
                'fecha_programada': actividad_data['fecha_programada'],
                'fecha_inicio': actividad_data['fecha_inicio'],
                'fecha_cierre':actividad_data['fecha_cierre'],
                'presupuesto':actividad_data['presupuesto'], 
                'presupuestoGlobal':actividad_data['presupuestoGlobal'], 
                'procedencia_fondos':actividad_data['procedencia_fondos'],
                'totalReportado':actividad_data['totalReportado'],
                'totalEjecutado':actividad_data['totalEjecutado'], 
                'saldo':actividad_data['saldo'], 
                'gradoEjecucion':actividad_data['gradoEjecucion'],
                'pei_id': actividad_data['pei'],
                'estaInactiva': actividad_data['estaInactiva'],
                'tareas': actividad_data['tareas_pei'],
                'responsable': actividad_data['responsable'],
            }
            data.append(actividad_formateada)

        return Response(data)    
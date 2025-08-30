from rest_framework import generics
from rest_framework.response import Response
from spme_actividades.models import Actividad
from .serializeractividadestareas import TareaActividad, ActividadSerializer

class ActividadConTareasListView(generics.ListAPIView):
    """
    Endpoint que retorna todas las actividades con sus tareas relacionadas
    """
    queryset = Actividad.objects.all().prefetch_related('tareas')
    serializer_class = ActividadSerializer
    
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
                'tareas': actividad_data['tareas']
            }
            data.append(actividad_formateada)
        
        return Response(data)

class ActividadConTareasDetailView(generics.RetrieveAPIView):
    """
    Endpoint que retorna una actividad específica con sus tareas
    """
    queryset = Actividad.objects.all().prefetch_related('tareas')
    serializer_class = ActividadSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Formatear la respuesta
        data = {
            'id': serializer.data['id'],
            'codigo': serializer.data['codigo'],
            'nombreCorto': serializer.data['nombreCorto'],
            'estado': serializer.data['estado'],
            'fecha_programada': serializer.data['fecha_programada'],
            'fecha_inicio': serializer.data['fecha_inicio'],
            'fecha_cierre':serializer.data['fecha_cierre'],
            'presupuesto':serializer.data['presupuesto'], 
            'presupuestoGlobal':serializer.data['presupuestoGlobal'], 
            'procedencia_fondos':serializer.data['procedencia_fondos'],
            'totalReportado':serializer.data['totalReportado'],
            'totalEjecutado':serializer.data['totalEjecutado'], 
            'saldo':serializer.data['saldo'], 
            'gradoEjecucion':serializer.data['gradoEjecucion'],
            'tareas': serializer.data['tareas']
        }
        
        return Response(data)
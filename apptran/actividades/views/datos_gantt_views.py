from rest_framework.decorators import api_view
from rest_framework.response import Response
from spme_actividades.models import Actividad
from ..serializador.datos_gantt_serializer import ActividadGanntSerializer

@api_view(['GET'])
def actividades_con_estados(request):
    # Definir los estados con sus colores
    estados_data = [
        {"id": "PLAN", "nombre": "Planificacion", "color": "#64b5f6"},
        {"id": "RETR", "nombre": "Retraso", "color": "#ff0000"},
        {"id": "REPROG", "nombre": "Reprogramacion", "color": "#ffd54f"},
        {"id": "EJEC", "nombre": "En_Ejecucion", "color": "#ffa726"},
        {"id": "REP", "nombre": "En_Reporte", "color": "#81c784"},
        {"id": "FIN", "nombre": "Finalizado", "color": "#003CFF"}
    ]
    
    # Obtener actividades que no estén inactivas
    actividades = Actividad.objects.filter(estaInactiva=False)
    
    # Serializar los datos
    serializer = ActividadGanntSerializer(actividades, many=True)
    
    # Preparar la respuesta
    response_data = {
        "estados": estados_data,
        "actividades": serializer.data
    }
    
    return Response(response_data)
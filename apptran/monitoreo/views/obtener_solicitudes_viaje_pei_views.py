from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from spme_monitoreo.models import SolicitudViajeActPei
from ..serializers.obtener_solicitudes_viaje_pei_serializer import SolicitudViajeActPeiSerializer

# from .models import SolicitudViajeActPei
# from .serializers import SolicitudViajeActPeiSerializer

@api_view(['POST'])
def filtrar_solicitudes_viaje(request):
    """
    Endpoint POST para filtrar solicitudes de viaje por actividad y tarea
    """
    # Obtener datos del request
    id_actividad = request.data.get('id_actividad')
    id_tarea = request.data.get('id_tarea')
    
    # Validar que se reciban ambos parámetros
    if not id_actividad or not id_tarea:
        return Response({
            "estado": "error",
            "mensaje": "Se requieren id_actividad e id_tarea"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Filtrar las solicitudes
    solicitudes = SolicitudViajeActPei.objects.filter(
        actividad_id=id_actividad,
        tarea_id=id_tarea
    )
    
    # Verificar si hay resultados
    if not solicitudes.exists():
        return Response({
            "estado": "exito",
            "solicitudes": [],
            "mensaje": "No se encontraron solicitudes de viaje"
        })
    
    # Serializar los datos
    serializer = SolicitudViajeActPeiSerializer(solicitudes, many=True)
    
    # Determinar mensaje según cantidad
    cantidad = solicitudes.count()
    if cantidad == 1:
        mensaje = "Solicitud de viaje encontrada exitosamente"
    else:
        mensaje = f"{cantidad} solicitudes de viaje encontradas exitosamente"
    
    # Retornar respuesta
    return Response({
        "estado": "exito",
        "solicitudes": serializer.data,
        "mensaje": mensaje
    })
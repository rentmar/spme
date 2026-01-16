from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from spme_monitoreo.models import SolicitudViajeActPei
from ..serializers.obtener_solicitudes_viaje_pei_serializer import SolicitudViajeActPeiSerializer

@api_view(['POST'])
def filtrar_solicitudes_viaje(request):
    """
    Endpoint POST para filtrar solicitudes de viaje por actividad y/o tarea
    Acepta:
    - {"id_actividad": id, "id_tarea": null}
    - {"id_actividad": null, "id_tarea": id}
    - {"id_actividad": id, "id_tarea": id}
    - {"id_actividad": null, "id_tarea": null} -> ERROR
    """
    
    def validar_y_convertir(valor, nombre_campo):
        """Valida y convierte un valor a entero si no es None"""
        if valor is None:
            return None
        try:
            return int(valor)
        except (ValueError, TypeError):
            raise ValueError(f"{nombre_campo} debe ser un número válido")
    
    try:
        # Obtener y validar datos
        id_actividad_raw = request.data.get('id_actividad')
        id_tarea_raw = request.data.get('id_tarea')
        
        # Convertir a enteros si no son None
        id_actividad = validar_y_convertir(id_actividad_raw, 'id_actividad')
        id_tarea = validar_y_convertir(id_tarea_raw, 'id_tarea')
        
    except ValueError as e:
        return Response({
            "estado": "error",
            "mensaje": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar que al menos un parámetro tenga valor
    if id_actividad is None and id_tarea is None:
        return Response({
            "estado": "error",
            "mensaje": "Se requiere al menos uno de los parámetros: id_actividad o id_tarea"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Construir query dinámico
    queryset = SolicitudViajeActPei.objects.all()
    
    if id_actividad is not None:
        queryset = queryset.filter(actividad_id=id_actividad)
    
    if id_tarea is not None:
        queryset = queryset.filter(tarea_id=id_tarea)
    
    # Verificar si hay resultados
    if not queryset.exists():
        return Response({
            "estado": "exito",
            "solicitudes": [],
            "mensaje": "No se encontraron solicitudes de viaje"
        })
    
    # Serializar los datos
    serializer = SolicitudViajeActPeiSerializer(queryset, many=True)
    
    # Determinar mensaje
    cantidad = queryset.count()
    mensaje = (
        "Solicitud de viaje encontrada exitosamente" 
        if cantidad == 1 
        else f"{cantidad} solicitudes de viaje encontradas exitosamente"
    )
    
    # Información sobre filtros aplicados
    filtros = {}
    if id_actividad is not None:
        filtros['id_actividad'] = id_actividad
    if id_tarea is not None:
        filtros['id_tarea'] = id_tarea
    
    return Response({
        "estado": "exito",
        "solicitudes": serializer.data,
        "mensaje": mensaje,
        "filtros_aplicados": filtros
    })
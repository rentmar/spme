from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_estructuracion_pei.models import Pei, ActividadPei
from ..serializers.listar_actividades_pei_serializer import ActividadPeiSerializer

@api_view(['GET'])
def actividades_pei_con_tareas(request, pei_id):
    """
    Endpoint para obtener todas las actividades de un PEI con sus tareas
    """
    try:
        # Verificar que el PEI existe
        pei = get_object_or_404(Pei, id=pei_id)
        
        # Obtener todas las actividades del PEI con sus tareas
        actividades = ActividadPei.objects.filter(
            pei_id=pei_id
        ).prefetch_related('tareas_pei').select_related(
            'tipo', 'responsable', 'pei'
        ).order_by('-fecha_programada')
        
        # Serializar los datos
        serializer = ActividadPeiSerializer(actividades, many=True)
        
        return Response({
            'success': True,
            'pei_id': pei_id,
            'pei_nombre': pei.nombre if hasattr(pei, 'nombre') else 'PEI',
            'total_actividades': actividades.count(),
            'actividades': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
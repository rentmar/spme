# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
#from .models import BitacoraIndicador
from spme_proyectos_reportes.models import BitacoraIndicador
#from .serializers import BitacoraIndicadorSerializer
from ..serializers.get_bitacora_id_tipo_serializers import BitacoraIndicadorSerializer


@api_view(['POST'])
def bitacoras_por_indicador(request):
    """
    Endpoint para obtener bitácoras por ID y tipo de indicador
    Body esperado:
    {
        "id": 5,
        "tipo": "indicadorog"
    }
    """
    indicador_id = request.data.get('id')
    tipo_indicador = request.data.get('tipo')
    
    # Validar parámetros requeridos
    if not indicador_id or not tipo_indicador:
        return Response(
            {'error': 'Los campos "id" y "tipo" son requeridos en el body'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar tipo de indicador
    tipos_validos = ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']
    if tipo_indicador not in tipos_validos:
        return Response(
            {'error': f'Tipo de indicador inválido. Valores válidos: {", ".join(tipos_validos)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Construir filtro según el tipo de indicador
        filtro = Q()
        
        if tipo_indicador == 'indicadorog':
            filtro = Q(indicadorog_id=indicador_id)
        elif tipo_indicador == 'indicadoroe':
            filtro = Q(indicadoroe_id=indicador_id)
        elif tipo_indicador == 'indicadorrog':
            filtro = Q(indicadorrog_id=indicador_id)
        elif tipo_indicador == 'indicadorroe':
            filtro = Q(indicadorroe_id=indicador_id)
        
        # Obtener bitácoras ordenadas por fecha (más recientes primero)
        bitacoras = BitacoraIndicador.objects.filter(filtro).order_by('-fechaBitacora')
        
        # Serializar datos
        serializer = BitacoraIndicadorSerializer(bitacoras, many=True)
        
        return Response({
            'count': bitacoras.count(),
            'results': serializer.data
        })
        
    except ValueError:
        return Response(
            {'error': 'El ID del indicador debe ser un número válido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error al obtener bitácoras: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
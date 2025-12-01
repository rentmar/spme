from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from spme_estructuracion_pei.models import Pei, ObjetivoPei, FactoresCriticos, IndicadorPeiCuantitativo, IndicadorPeiCualitativo
from ..serializador.obtener_estructura_pei_serializer import PeiEstructuraSerializer

@api_view(['GET'])
def estructura_pei_completa(request, pei_id):
    """
    Endpoint para obtener la estructura completa de un PEI
    Incluye: objetivos, factores críticos, indicadores cuantitativos y cualitativos
    """
    try:
        # Prefetch optimizado para cada tipo de relación
        objetivos_prefetch = ObjetivoPei.objects.prefetch_related(
            Prefetch('factores_criticos', queryset=FactoresCriticos.objects.all()),
            Prefetch('indicador_pei_objetivo', 
                    queryset=IndicadorPeiCuantitativo.objects.all(), 
                    to_attr='indicadores_cuantitativos_prefetch'),
            Prefetch('indicador_pei_objetivo', 
                    queryset=IndicadorPeiCualitativo.objects.all(), 
                    to_attr='indicadores_cualitativos_prefetch')
        )
        
        # Obtener el PEI con toda la estructura relacionada
        pei = get_object_or_404(
            Pei.objects.prefetch_related(
                Prefetch('pei_obj_general', queryset=objetivos_prefetch)
            ),
            id=pei_id
        )
        
        # Serializar los datos
        serializer = PeiEstructuraSerializer(pei)
        
        return Response({
            'success': True,
            'pei': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Pei.DoesNotExist:
        return Response({
            'success': False,
            'error': f'PEI con id {pei_id} no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
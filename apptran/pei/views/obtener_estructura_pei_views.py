# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from spme_estructuracion_pei.models import (
    Pei,
    ObjetivoPei,
    IndicadorPeiCualitativo,
    IndicadorPeiCuantitativo
)
from ..serializador.obtener_estructura_pei_serializer import PeiSerializer


@api_view(['GET'])
def estructura_pei(request, pei_id=None):
    """
    Endpoint que combina indicadores cuantitativos y cualitativos
    """
    try:
        if pei_id:
            # Optimizar con Prefetch específico para cada tipo
            pei = get_object_or_404(
                Pei.objects.prefetch_related(
                    Prefetch(
                        'pei_obj_general',
                        queryset=ObjetivoPei.objects.prefetch_related(
                            'factores_criticos',
                            Prefetch(
                                'indicador_pei_objetivo',
                                queryset=IndicadorPeiCuantitativo.objects.all(),
                                to_attr='prefetched_cuantitativos'
                            ),
                            Prefetch(
                                'indicador_pei_objetivo',
                                queryset=IndicadorPeiCualitativo.objects.all(),
                                to_attr='prefetched_cualitativos'
                            )
                        )
                    )
                ),
                id=pei_id
            )
            
            serializer = PeiSerializer(pei)
            return Response({
                "PEI": serializer.data
            })
            
        else:
            # Para todos los PEIs (menos optimizado pero funcional)
            peis = Pei.objects.all().prefetch_related(
                'pei_obj_general__factores_criticos'
            )
            
            serializer = PeiSerializer(peis, many=True)
            return Response({
                "PEIs": serializer.data
            })
            
    except Exception as e:
        import traceback
        return Response({
            "error": str(e),
            "detail": "Error al generar la estructura del PEI"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Versión simple y directa (recomendada)
@api_view(['GET'])
def estructura_pei_simple(request, pei_id=None):
    """
    Versión simple que funciona con el serializador combinado
    """
    try:
        if pei_id:
            pei = get_object_or_404(Pei, id=pei_id)
            serializer = PeiSerializer(pei)
            return Response({
                "PEI": serializer.data
            })
        else:
            peis = Pei.objects.all()
            serializer = PeiSerializer(peis, many=True)
            return Response({
                "PEIs": serializer.data
            })
            
    except Exception as e:
        return Response({
            "error": f"Error: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
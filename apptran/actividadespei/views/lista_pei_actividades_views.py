# views.py
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from spme_estructuracion_pei.models import (
    Pei,
    ActividadPei,
    ObjetivoPei,
    FactoresCriticos,
    IndicadorPeiCualitativo,
    IndicadorPeiCuantitativo,
)
from ..serializers.lista_pei_actividades_serializer import PeiSerializer, ActividadPeiSerializer

@api_view(['GET'])
def pei_detalle_actividades(request, pei_id):
    """
    Endpoint que retorna un PEI específico con todas sus actividades
    """
    try:
        # Obtener el PEI
        pei = Pei.objects.get(id=pei_id)
        
        # Prefetch de relaciones para optimizar consultas
        actividades = ActividadPei.objects.filter(pei=pei).select_related(
            'responsable'  # Optimización para el responsable
        ).prefetch_related(
            'objetivos_pei',
            'factores_criticos',
            'indicadores_cuantitativos',
            'indicadores_cualitativos'
        )
        
        # Serializar los datos
        pei_data = {
            'id': pei.id,
            'titulo': pei.titulo,
            'descripcion': pei.descripcion if hasattr(pei, 'descripcion') else ''
        }
        
        actividades_data = ActividadPeiSerializer(actividades, many=True).data
        
        # Estructurar la respuesta
        response_data = {
            'pei': pei_data,
            'actividades': actividades_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Pei.DoesNotExist:
        return Response(
            {'error': 'PEI no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# Versión con Class-Based View
class PeiConActividadesAPIView(generics.RetrieveAPIView):
    """
    Class-Based View para el endpoint de PEI con actividades
    """
    
    def get(self, request, *args, **kwargs):
        pei_id = kwargs.get('pei_id')
        
        try:
            pei = Pei.objects.get(id=pei_id)
            
            # Obtener actividades con todas las relaciones optimizadas
            actividades = ActividadPei.objects.filter(
                pei=pei
            ).select_related('responsable').prefetch_related(
                Prefetch('objetivos_pei', queryset=ObjetivoPei.objects.all()),
                Prefetch('factores_criticos', queryset=FactoresCriticos.objects.all()),
                Prefetch('indicadores_cuantitativos', queryset=IndicadorPeiCuantitativo.objects.all()),
                Prefetch('indicadores_cualitativos', queryset=IndicadorPeiCualitativo.objects.all())
            )
            
            # Preparar datos del PEI
            pei_data = {
                'id': pei.id,
                'titulo': pei.titulo,
                'descripcion': getattr(pei, 'descripcion', '')
            }
            
            # Serializar actividades
            actividades_serializer = ActividadPeiSerializer(actividades, many=True)
            
            return Response({
                'pei': pei_data,
                'actividades': actividades_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Pei.DoesNotExist:
            return Response(
                {'error': 'PEI no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
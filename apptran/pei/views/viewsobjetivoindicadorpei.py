# En tu archivo views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from spme_estructuracion_pei.models import Pei, ObjetivoPei, IndicadorPeiBase
#from .models import Pei, ObjetivoPei
#from .serializers import ObjetivoPeiSerializer
from ..serializador.serializadorobjetivoindicadorpei import ObjetivoPeiSerializer, IndicadorPeiBaseSerializer, IndicadorPeiSerializer

class ObjetivoPeiPorPeiListView(generics.ListAPIView):
    """
    Endpoint para obtener todos los Objetivos PEI filtrados por ID de PEI
    """
    serializer_class = ObjetivoPeiSerializer
    
    def get_queryset(self):
        pei_id = self.kwargs['pei_id']
        return ObjetivoPei.objects.filter(pei_id=pei_id)
    
    def list(self, request, *args, **kwargs):
        try:
            pei_id = self.kwargs['pei_id']
            # Verificar si el PEI existe
            get_object_or_404(Pei, id=pei_id)
            
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'success': True,
                'count': queryset.count(),
                'data': serializer.data
            })
            
        except Pei.DoesNotExist:
            return Response({
                'success': False,
                'error': f'PEI con ID {pei_id} no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        

class IndicadorPeiPorPeiListView(generics.ListAPIView):
    """
    Endpoint para obtener todos los Indicadores PEI filtrados por ID de PEI
    """
    serializer_class = IndicadorPeiSerializer
    
    def get_queryset(self):
        pei_id = self.kwargs['pei_id']
        # Filtrar indicadores a través de la relación objetivo → pei
        return IndicadorPeiBase.objects.filter(objetivo__pei_id=pei_id)
    
    def list(self, request, *args, **kwargs):
        try:
            pei_id = self.kwargs['pei_id']
            # Verificar si el PEI existe
            get_object_or_404(Pei, id=pei_id)
            
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'success': True,
                'count': queryset.count(),
                'data': serializer.data
            })
            
        except Pei.DoesNotExist:
            return Response({
                'success': False,
                'error': f'PEI con ID {pei_id} no existe'
            }, status=status.HTTP_404_NOT_FOUND)        
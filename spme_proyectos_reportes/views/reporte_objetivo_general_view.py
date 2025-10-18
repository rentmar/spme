from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from ..services.generators.objetivo_general_generator import ObjetivoGeneralGenerator

class ReporteObjetivoGeneralViewSet(viewsets.ViewSet):
    """
    ViewSet específico para generación de reportes de Objetivos Generales
    """
    
    @action(detail=True, methods=['get'])
    def descargar_reporte(self, request, pk=None):
        """Descarga SOLO el reporte del objetivo general (sin encadenar)"""
        try:
            generator = ObjetivoGeneralGenerator()
            return generator.generar_y_descargar_individual(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=404)
        except Exception as e:
            return Response({'error': f'Error generando reporte: {str(e)}'}, status=500)
    
    @action(detail=True, methods=['get'])
    def informacion_reporte(self, request, pk=None):
        """Obtiene metadatos del objetivo general"""
        from spme_estructuracion_proyecto.models import ObjetivoGeneralProyecto
        
        try:
            objetivo_general = ObjetivoGeneralProyecto.objects.get(id=pk)
            return Response({
                'modelo': 'objetivogeneral',
                'nivel': 2,
                'id': objetivo_general.id,
                'codigo': objetivo_general.codigo,
                'descripcion': objetivo_general.descripcion[:100] + '...' if objetivo_general.descripcion else '',
                'proyecto_asociado': {
                    'id': objetivo_general.proyecto.id,
                    'codigo': objetivo_general.proyecto.codigo,
                    'titulo': objetivo_general.proyecto.titulo
                }
            })
        except ObjetivoGeneralProyecto.DoesNotExist:
            return Response({'error': 'Objetivo General no encontrado'}, status=404)
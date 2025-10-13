from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from ..services.generators.proyecto_generator import ProyectoGenerator


class ReporteProyectoViewSet(viewsets.ViewSet):
    """
    ViewSet para generación de reportes de Proyectos (Nivel 1)
    """
    
    @action(detail=True, methods=['get'])
    def descargar_reporte(self, request, pk=None):
        """Endpoint para descargar reporte individual del proyecto"""
        try:
            generator = ProyectoGenerator()
            return generator.generar_y_descargar(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=404)
        except Exception as e:
            return Response({'error': f'Error generando reporte: {str(e)}'}, status=500)
    
    @action(detail=True, methods=['get'])
    def informacion_reporte(self, request, pk=None):
        """Endpoint para obtener metadatos del reporte disponible"""
        from spme_estructuracion_proyecto.models import Proyecto
        
        try:
            proyecto = Proyecto.objects.get(id=pk)
            return Response({
                'modelo': 'Proyecto',
                'nivel': 1,
                'id': proyecto.id,
                'codigo': proyecto.codigo,
                'titulo': proyecto.titulo,
                'niveles_inferiores': [
                    'objetivogeneral',
                    'objetivoespecifico'
                ]
            })
        except Proyecto.DoesNotExist:
            return Response({'error': 'Proyecto no encontrado'}, status=404)
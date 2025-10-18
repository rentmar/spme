from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import os
import django

# Configurar Django explícitamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

# Importación CORREGIDA - nota el plural "composers"
from ..services.composer.chain_composer import ChainComposer

class ReporteEncadenadoViewSet(viewsets.ViewSet):
    """
    ViewSet unificado para generación de reportes encadenados desde cualquier nivel
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.composer = ChainComposer()
    
    @action(detail=False, methods=['post'], url_path='generar-desde-modelo')
    def generar_desde_modelo(self, request):
        """
        Genera reporte encadenado desde cualquier modelo
        Body: {
            "modelo": "proyecto",
            "id": 1,
            "profundidad": 2
        }
        """
        modelo = request.data.get('modelo')
        objeto_id = request.data.get('id')
        profundidad = request.data.get('profundidad', 2)
        
        if not modelo or not objeto_id:
            return Response(
                {'error': 'Se requieren los campos "modelo" e "id"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            return self.composer.generar_y_descargar(
                modelo=modelo,
                objeto_id=objeto_id,
                profundidad=profundidad
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': f'Error generando reporte: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='metadatos/(?P<modelo>[^/.]+)/(?P<objeto_id>[^/.]+)')
    def obtener_metadatos(self, request, modelo=None, objeto_id=None):
        """Obtiene metadatos de reporte para un modelo específico"""
        if not modelo or not objeto_id:
            return Response(
                {'error': 'Se requieren modelo e ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Método simplificado ya que obtener_metadatos_reporte no existe
        try:
            from spme_estructuracion_proyecto.models import Proyecto, ObjetivoGeneralProyecto
            
            if modelo == 'proyecto':
                obj = Proyecto.objects.get(id=objeto_id)
                metadatos = {
                    'modelo': 'proyecto',
                    'nivel': 1,
                    'id': obj.id,
                    'codigo': obj.codigo,
                    'titulo': obj.titulo,
                    'relaciones_disponibles': ['objetivogeneral']
                }
            elif modelo == 'objetivogeneral':
                obj = ObjetivoGeneralProyecto.objects.get(id=objeto_id)
                metadatos = {
                    'modelo': 'objetivogeneral',
                    'nivel': 2,
                    'id': obj.id,
                    'codigo': obj.codigo,
                    'descripcion': obj.descripcion[:100] + '...' if obj.descripcion else '',
                    'relaciones_disponibles': []
                }
            else:
                return Response(
                    {'error': f'Modelo {modelo} no soportado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(metadatos)
            
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo metadatos: {str(e)}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def modelos_disponibles(self, request):
        """Lista todos los modelos disponibles para generación de reportes"""
        modelos = [
            {
                'modelo': 'proyecto',
                'nivel': 1,
                'relaciones': ['objetivogeneral'],
                'descripcion': 'Reporte de Proyecto con encadenamiento a Objetivos Generales'
            },
            {
                'modelo': 'objetivogeneral',
                'nivel': 2, 
                'relaciones': [],
                'descripcion': 'Reporte individual de Objetivo General'
            }
        ]
        
        return Response({'modelos_disponibles': modelos})
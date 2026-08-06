# spme/spme_tree_reporter/views/generar_reporte_proyecto_view.py
"""
Endpoint para generación de reportes Word concatenados.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse


from ..serializers.generar_reporte_serializer import GenerarReporteSerializer
from ..services.reporte_proyecto_service import ReporteProyectoService


class GenerarReporteProyectoView(APIView):
    """
    GET /api/reportes/generar/
    
    Genera un reporte Word concatenado recorriendo el árbol jerárquico.
    
    Parámetros:
        nodo: str (default: 'proyecto')
              Tipo de nodo inicial
        id: int (requerido)
            ID del nodo
        tipo: str (default: 'completo')
              'completo' | 'ejecutivo' | 'gerencial' | 'operativo' | 'ficha_tecnica' | 'personalizado'
        profundidad: str (default: 'all')
                     'self' | '1' | '2' | '3' | '4' | 'all'
                     Solo aplica cuando tipo='personalizado'
        modo_actividades: str (default: 'anexo')
                          'omitir' | 'referencia' | 'anexo'
                          Solo aplica cuando tipo='personalizado'
        incluir_portada: bool (default: true)
        incluir_indice: bool (default: true)
    
    Ejemplos:
        # Reporte completo del proyecto 48
        GET /api/reportes/generar/?nodo=proyecto&id=48&tipo=completo
        
        # Reporte ejecutivo
        GET /api/reportes/generar/?nodo=proyecto&id=48&tipo=ejecutivo
        
        # Ficha técnica (solo el proyecto, sin hijos)
        GET /api/reportes/generar/?nodo=proyecto&id=48&tipo=ficha_tecnica
        
        # Reporte personalizado: solo 2 niveles, sin actividades
        GET /api/reportes/generar/?nodo=proyecto&id=48&tipo=personalizado&profundidad=2&modo_actividades=omitir
        
        # Reporte desde un objetivo específico
        GET /api/reportes/generar/?nodo=objetivoespecificoog&id=50&tipo=personalizado&profundidad=all
        
        # Reporte de una actividad
        GET /api/reportes/generar/?nodo=actividad&id=98&tipo=personalizado&profundidad=all
    """
    
    def get(self, request):
        # 1. Validar parámetros
        serializer = GenerarReporteSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Parámetros inválidos', 'detalles': serializer.errors},
                status=400
            )
        
        config = serializer.get_config()
        
        # 2. Generar reporte
        service = ReporteProyectoService()
        
        try:
            if config['tipo'] == 'personalizado':
                # Modo personalizado: usar todos los parámetros
                buffer = service.generar_reporte(
                    tipo_nodo=config['tipo_nodo'],
                    nodo_id=config['nodo_id'],
                    profundidad=config['profundidad'],
                    modo_actividades=config['modo_actividades'],
                    incluir_portada=config['incluir_portada'],
                    incluir_indice=config['incluir_indice'],
                )
            else:
                # Modo predefinido: usar configuración por tipo
                buffer = service.generar_reporte_predefinido(
                    tipo_nodo=config['tipo_nodo'],
                    nodo_id=config['nodo_id'],
                    tipo=config['tipo'],
                )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=404
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error al generar el reporte: {str(e)}', 'traceback': traceback.format_exc()},
                status=500
            )
        
        # 3. Preparar respuesta
        filename = service.get_filename(config['tipo_nodo'], config['nodo_id'], config['tipo'])

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response 
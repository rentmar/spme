# services/views/actividad_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.generators.actividad_generator import ActividadGenerator
#from ..generators.actividad_generator import ActividadGenerator
from spme_actividades.models import Actividad

class ActividadReportView(APIView):
    """Vista para generar reportes de actividad (solo primera parte)"""
    
    def get(self, request, actividad_id=None):
        try:
            if actividad_id:
                # Generar reporte de actividad
                generator = ActividadGenerator()
                buffer = generator.generar_reporte_actividad(actividad_id)
                
                # Crear respuesta HTTP
                response = HttpResponse(
                    buffer.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = f'attachment; filename="reporte_actividad_{actividad_id}.docx"'
                return response
            else:
                # Listar actividades disponibles
                actividades = Actividad.objects.all()[:50]  # Límite por seguridad
                data = [{
                    'id': a.id,
                    'codigo': a.codigo,
                    'nombreCorto': a.nombreCorto,
                    'estado': a.get_estado_display(),
                    'fecha_programada': a.fecha_programada,
                    'proyecto': a.proyecto.codigo if a.proyecto else None,
                    'responsable': a.responsable.get_full_name() if a.responsable else None
                } for a in actividades]
                
                return Response({
                    'actividades': data,
                    'total': len(data),
                    'endpoint_reporte': '/api/actividades/reporte/{id}/'
                })
                
        except Actividad.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generando reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

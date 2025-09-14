# views/reporte_actividad_view.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.shortcuts import get_object_or_404
#from ..models import Actividad
from spme_actividades.models import Actividad
from ..services.reporte_actividad_service import ReporteActividadService
from ..serializers.actividad_reporte_serializer import ActividadReporteSerializer
import os

@api_view(['GET'])
def generar_reporte_actividad(request, actividad_id):
    """
    Genera un reporte Word para una actividad específica
    """
    try:
        # Obtener la actividad
        actividad = get_object_or_404(Actividad, id=actividad_id)
        
        # Generar el reporte
        reporte_service = ReporteActividadService(actividad)
        temp_file = reporte_service.generar_reporte_actividad()
        
        # Preparar respuesta
        filename = f"reporte_actividad_{actividad.codigo}_{actividad.id}.docx"
        
        response = FileResponse(
            open(temp_file.name, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Limpiar archivo temporal después de enviar la respuesta
        def cleanup_temp_file():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        response.closed = cleanup_temp_file
        
        return response
        
    except Exception as e:
        return Response(
            {
                'error': 'Error al generar reporte de actividad',
                'detalles': str(e),
                'actividad_id': actividad_id
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def info_reporte_actividad(request, actividad_id):
    """
    Devuelve información sobre la actividad para el reporte
    """
    try:
        actividad = get_object_or_404(Actividad, id=actividad_id)
        serializer = ActividadReporteSerializer(actividad)
        
        return Response({
            'actividad_id': actividad.id,
            'codigo': actividad.codigo,
            'nombre': actividad.nombreCorto,
            'estado': actividad.get_estado_display(),
            'proyecto': actividad.proyecto.codigo if actividad.proyecto else None,
            'tiene_tareas': actividad.tareas.exists(),
            'puede_generar_reporte': True,
            'datos': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': 'Error al obtener información del reporte',
            'detalles': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
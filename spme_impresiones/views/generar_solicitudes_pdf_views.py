from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso,
    SolicitudViaje, 
    SolicitudPagoDirecto,
    RendicionCuentas,
)

from ..services import PDFGeneratorFactory, SolicitudFondosTareaPDFGenerator

class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para generar reportes de diferentes tipos
    """
    # permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='solicitud-fondos/(?P<pk>[^/.]+)')
    def solicitud_fondos(self, request, pk=None):
        """
        Generar reporte de solicitud de fondos
        """
        try:
            solicitud = get_object_or_404(SolicitudFondos, pk=pk)
            response = PDFGeneratorFactory.generate_pdf(solicitud)
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='solicitud-reembolso/(?P<pk>[^/.]+)')
    def solicitud_reembolso(self, request, pk=None):
        """
        Generar reporte de solicitud de reembolso
        """
        try:
            solicitud = get_object_or_404(SolicitudReembolso, pk=pk)
            response = PDFGeneratorFactory.generate_pdf(solicitud)
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='solicitud-viaje/(?P<pk>[^/.]+)')
    def solicitud_viaje(self, request, pk=None):
        """
        Generar reporte de solicitud de viaje
        """
        try:
            solicitud = get_object_or_404(SolicitudViaje, pk=pk)
            response = PDFGeneratorFactory.generate_pdf(solicitud)
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
     
    @action(detail=False, methods=['get'], url_path='solicitud-pago-directo/(?P<pk>[^/.]+)')
    def solicitud_pago_directo(self, request, pk=None):
        """
        Generar reporte de solicitud de pago directo
        """
        try:
            solicitud = get_object_or_404(SolicitudPagoDirecto, pk=pk)
            response = PDFGeneratorFactory.generate_pdf(solicitud)
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='rendicion-cuentas/(?P<pk>[^/.]+)')
    def rendicion_cuentas(self, request, pk=None):
        """
        Generar reporte de rendición de cuentas
        """
        try:
            rendicion = get_object_or_404(RendicionCuentas, pk=pk)
            response = PDFGeneratorFactory.generate_pdf(rendicion)
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def solicitud_fondos_tarea(self, request, pk=None):
        """
        Generar reporte ESPECÍFICO para solicitud de fondos CON TAREA
        """
        try:
            solicitud = get_object_or_404(SolicitudFondos, pk=pk)
            
            if not solicitud.tarea:
                return Response(
                    {
                        'error': 'Documento específico para tarea no aplicable',
                        'message': 'Esta solicitud de fondos no tiene una tarea asociada.',
                        'solicitud_id': solicitud.id,
                        'numero_formulario': solicitud.numeroFormulario,
                        'recomendacion': 'Use el endpoint estándar: /api/impresiones/solicitud-fondos/{id}/pdf/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            generator = SolicitudFondosTareaPDFGenerator()
            response = generator.generate(solicitud)
            
            return response
            
        except SolicitudFondos.DoesNotExist:
            return Response(
                {'error': f'Solicitud de fondos con ID {pk} no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de tarea: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
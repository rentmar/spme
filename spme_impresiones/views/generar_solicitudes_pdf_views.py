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

from ..services import PDFGeneratorFactory




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
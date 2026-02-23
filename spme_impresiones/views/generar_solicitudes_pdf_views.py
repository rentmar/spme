#views/generar_solicitudes_pdf_views
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
    SolicitudFondosActPei,
)

from ..services import (
    PDFGeneratorFactory, 
    SolicitudFondosTareaPDFGenerator, 
    SolicitudReembolsoTareaPDFGenerator,
    SolicitudViajeTareaPDFGenerator,
    SolicitudPagoDirectoTareaPDFGenerator,
    RendicionCuentasTareaPDFGenerator,
    )

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
        
    @action(detail=False, methods=['get'], url_path='solicitud-fondos-tarea/(?P<pk>[^/.]+)')
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
        
    @action(detail=False, methods=['get'], url_path='solicitud-reembolso-tarea/(?P<pk>[^/.]+)')
    def solicitud_reembolso_tarea(self, request, pk=None):
        """
        Generar reporte ESPECÍFICO para solicitud de reembolso CON TAREA
        """
        try:
            solicitud = get_object_or_404(SolicitudReembolso, pk=pk)
            
            # Verificar que tenga tarea asociada
            if not solicitud.tarea:
                return Response(
                    {
                        'error': 'Documento específico para tarea no aplicable',
                        'message': 'Esta solicitud de reembolso no tiene una tarea asociada.',
                        'solicitud_id': solicitud.id,
                        'numero_formulario': solicitud.numeroFormulario,
                        'recomendacion': 'Use el endpoint estándar: /api/impresiones/solicitud-reembolso/{id}/pdf/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar el generador específico para reembolso de tareas
            generator = SolicitudReembolsoTareaPDFGenerator()
            response = generator.generate(solicitud)
            
            return response
            
        except SolicitudReembolso.DoesNotExist:
            return Response(
                {'error': f'Solicitud de reembolso con ID {pk} no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte de reembolso de tarea: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'], url_path='solicitud-viaje-tarea/(?P<pk>[^/.]+)')
    def solicitud_viaje_tarea(self, request, pk=None):
        """
        Generar reporte ESPECÍFICO para solicitud de viaje CON TAREA
        """
        try:
            # Intentar convertir pk a entero
            try:
                solicitud_id = int(pk)
            except ValueError:
                return Response(
                    {
                        'error': 'ID inválido',
                        'message': f'El ID "{pk}" no es un número válido'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si existe la solicitud
            try:
                solicitud = SolicitudViaje.objects.get(pk=solicitud_id)
            except SolicitudViaje.DoesNotExist:
                return Response(
                    {
                        'error': 'Solicitud no encontrada',
                        'message': f'No existe una SolicitudViaje con ID {solicitud_id}'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tenga tarea asociada
            if not solicitud.tarea:
                return Response(
                    {
                        'error': 'Documento específico para tarea no aplicable',
                        'message': 'Esta solicitud de viaje no tiene una tarea asociada.',
                        'solicitud_id': solicitud.id,
                        'numero_formulario': solicitud.numeroFormulario,
                        'recomendacion': 'Use el endpoint estándar: /api/impresiones/solicitud-viaje/{id}/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar el generador específico para viaje de tareas
            generator = SolicitudViajeTareaPDFGenerator()
            response = generator.generate(solicitud)
            
            return response
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar reporte de viaje de tarea',
                    'message': str(e),
                    'tipo_error': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    


    @action(detail=False, methods=['get'], url_path='solicitud-pago-directo-tarea/(?P<pk>[^/.]+)')
    def solicitud_pago_directo_tarea(self, request, pk=None):
        """
        Generar reporte ESPECÍFICO para solicitud de pago directo CON TAREA
        """
        try:
            # Intentar convertir pk a entero
            try:
                solicitud_id = int(pk)
            except ValueError:
                return Response(
                    {
                        'error': 'ID inválido',
                        'message': f'El ID "{pk}" no es un número válido'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si existe la solicitud
            try:
                solicitud = SolicitudPagoDirecto.objects.get(pk=solicitud_id)
            except SolicitudPagoDirecto.DoesNotExist:
                return Response(
                    {
                        'error': 'Solicitud no encontrada',
                        'message': f'No existe una SolicitudPagoDirecto con ID {solicitud_id}'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tenga tarea asociada
            if not solicitud.tarea:
                return Response(
                    {
                        'error': 'Documento específico para tarea no aplicable',
                        'message': 'Esta solicitud de pago directo no tiene una tarea asociada.',
                        'solicitud_id': solicitud.id,
                        'numero_formulario': solicitud.numeroFormulario,
                        'recomendacion': 'Use el endpoint estándar: /api/impresiones/solicitud-pago-directo/{id}/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar el generador específico para pago directo de tareas
            generator = SolicitudPagoDirectoTareaPDFGenerator()
            response = generator.generate(solicitud)
            
            return response
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar reporte de pago directo de tarea',
                    'message': str(e),
                    'tipo_error': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    
        

    @action(detail=False, methods=['get'], url_path='rendicion-cuentas-tarea/(?P<pk>[^/.]+)')
    def rendicion_cuentas_tarea(self, request, pk=None):
        """
        Generar reporte ESPECÍFICO para rendición de cuentas CON TAREA
        """
        try:
            # Intentar convertir pk a entero
            try:
                rendicion_id = int(pk)
            except ValueError:
                return Response(
                    {
                        'error': 'ID inválido',
                        'message': f'El ID "{pk}" no es un número válido'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si existe la rendición
            try:
                rendicion = RendicionCuentas.objects.get(pk=rendicion_id)
            except RendicionCuentas.DoesNotExist:
                return Response(
                    {
                        'error': 'Rendición no encontrada',
                        'message': f'No existe una RendicionCuentas con ID {rendicion_id}'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que tenga tarea asociada
            if not rendicion.tarea:
                return Response(
                    {
                        'error': 'Documento específico para tarea no aplicable',
                        'message': 'Esta rendición de cuentas no tiene una tarea asociada.',
                        'rendicion_id': rendicion.id,
                        'numero_formulario': rendicion.numeroFormulario,
                        'recomendacion': 'Use el endpoint estándar: /api/impresiones/rendicion-cuentas/{id}/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar el generador específico para rendición de cuentas de tareas
            generator = RendicionCuentasTareaPDFGenerator()
            response = generator.generate(rendicion)
            
            return response
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar reporte de rendición de cuentas de tarea',
                    'message': str(e),
                    'tipo_error': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  

    # views/generar_solicitudes_pdf_views.py
    @action(detail=False, methods=['get'], url_path='solicitud-fondos-actividad-pei/(?P<pk>[^/.]+)')
    def solicitud_fondos_actividad_pei(self, request, pk=None):
        solicitud = get_object_or_404(SolicitudFondosActPei, pk=pk)
        if solicitud.tarea:
            return Response({'error': 'Use endpoint para tareas'}, status=400)
        return PDFGeneratorFactory.generate_pdf(solicitud)    

    @action(detail=False, methods=['get'], url_path='solicitud-fondos-tarea-pei/(?P<pk>[^/.]+)')
    def solicitud_fondos_tarea_pei(self, request, pk=None):
        """
        Generar reporte de solicitud de fondos para TAREA PEI (con tarea)
        """
        try:
            solicitud = get_object_or_404(SolicitudFondosActPei, pk=pk)
            
            # Validar que sea una solicitud de tarea
            if not solicitud.tarea:
                return Response(
                    {
                        'error': 'Tipo de documento incorrecto',
                        'message': 'Esta solicitud no tiene una tarea asociada. Use el endpoint para actividades.',
                        'recomendacion': f'/api/impresiones/solicitud-fondos-actividad-pei/{pk}/'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # USAR EL GENERADOR DIRECTAMENTE (NO la fábrica)
            from ..services.solicitud_fondos_tarea_pei_pdf import SolicitudFondosTareaPeiPDFGenerator
            generator = SolicitudFondosTareaPeiPDFGenerator()
            response = generator.generate(solicitud)
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
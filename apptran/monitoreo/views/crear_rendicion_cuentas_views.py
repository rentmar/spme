# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from spme_monitoreo.models import RendicionCuentas
from ..serializers.crear_rendicion_cuentas_serializer import RendicionCuentasCreateSerializer

@api_view(['POST'])
def crear_rendicion_cuentas(request):
    """
    Endpoint para crear una nueva rendición de cuentas
    El usuario es referencial, no necesita coincidir con la sesión
    """
    try:
        data = request.data.copy()
        
        serializer = RendicionCuentasCreateSerializer(data=data)
        
        if serializer.is_valid():
            rendicion = serializer.save()
            
            # Respuesta exitosa
            response_data = {
                'success': True,
                'message': 'Rendición de cuentas creada exitosamente',
                'id': rendicion.id,
                'numeroFormulario': rendicion.numeroFormulario,
                'usuario_id': rendicion.usuario.id if rendicion.usuario else None,
                'solicitud_fondos_id': rendicion.solicitudFondos.id if rendicion.solicitudFondos else None,
                'solicitud_reembolso_id': rendicion.solicitudReembolso.id if rendicion.solicitudReembolso else None,
                'solicitud_viaje_id': rendicion.solicitudViaje.id if rendicion.solicitudViaje else None,
                'solicitud_pago_directo_id': rendicion.solicitudPagoDirecto.id if rendicion.solicitudPagoDirecto else None,
                'actividad_id': rendicion.actividad.id if rendicion.actividad else None,
                'tarea_id': rendicion.tarea.id if rendicion.tarea else None
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Error en los datos de la rendición',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
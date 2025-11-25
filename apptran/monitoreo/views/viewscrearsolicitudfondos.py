
# views.py 
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db import transaction
from spme_monitoreo.models import SolicitudFondos
from ..serializers.serializercrearsolicitudfondos import SolicitudFondosCreateSerializer

@api_view(['POST']) 
@permission_classes([AllowAny])
def crear_solicitud_fondos(request):
    """
    Endpoint POST para crear una nueva solicitud de fondos con transacción atómica
    que involucra la actualización de Actividad y creación de SolicitudFondos
    """
    serializer = SolicitudFondosCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # La transacción está manejada dentro del serializador con @transaction.atomic
            solicitud = serializer.save()
            
            # Preparar respuesta con todos los campos relevantes
            response_data = {
                'success': True,
                'message': 'Solicitud de fondos creada exitosamente',
                'id': solicitud.id,
                'numero_formulario': solicitud.numeroFormulario,
                'actividad_actualizada': hasattr(solicitud, 'actividad') and solicitud.actividad is not None,
                'actividad_id': solicitud.actividad.id if solicitud.actividad else None,
                'tarea_id': solicitud.tarea.id if solicitud.tarea else None,
                # INCLUIR LOS NUEVOS CAMPOS EN LA RESPUESTA
                'descripcion_actividad': solicitud.descripcion_actividad,
                'objetivo_actividad': solicitud.objetivo_actividad,
                'datos_forma_pago': solicitud.datos_forma_pago,
            }
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:  # CORREGIDO: Usar ValidationError importado
            # Errores de validación del serializador
            return Response(
                {
                    'success': False,
                    'message': 'Error de validación en los datos',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            # Errores generales (la transacción se revertirá automáticamente)
            return Response(
                {
                    'success': False,
                    'message': f'Error inesperado al procesar la solicitud: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Errores de validación del serializer
    return Response(
        {
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# @api_view(['POST']) 
# @permission_classes([AllowAny])
# def crear_solicitud_fondos(request):
#     """
#     Endpoint POST para crear una nueva solicitud de fondos con transacción atómica
#     que involucra la actualización de Actividad y creación de SolicitudFondos
#     """
#     serializer = SolicitudFondosCreateSerializer(data=request.data)
    
#     if serializer.is_valid():
#         try:
#             # La transacción está manejada dentro del serializador con @transaction.atomic
#             solicitud = serializer.save()
            
#             return Response(
#                 {
#                     'success': True,
#                     'message': 'Solicitud de fondos creada exitosamente',
#                     'id': solicitud.id,
#                     'numero_formulario': solicitud.numeroFormulario,
#                     'actividad_actualizada': hasattr(solicitud, 'actividad') and solicitud.actividad is not None,
#                     'actividad_id': solicitud.actividad.id if solicitud.actividad else None,
#                     'tarea_id': solicitud.tarea.id if solicitud.tarea else None,
#                 },
#                 status=status.HTTP_201_CREATED
#             )
            
#         except serializer.ValidationError as e:
#             # Errores de validación del serializador
#             return Response(
#                 {
#                     'success': False,
#                     'message': 'Error de validación en los datos',
#                     'errors': e.detail
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
            
#         except Exception as e:
#             # Errores generales (la transacción se revertirá automáticamente)
#             return Response(
#                 {
#                     'success': False,
#                     'message': f'Error inesperado al procesar la solicitud: {str(e)}'
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     # Errores de validación del serializer
#     return Response(
#         {
#             'success': False,
#             'message': 'Datos inválidos',
#             'errors': serializer.errors
#         },
#         status=status.HTTP_400_BAD_REQUEST
#     )




# @api_view(['POST'])
# @permission_classes([AllowAny])  # Permite acceso sin autenticación
# def crear_solicitud_fondos(request):
#     """
#     Endpoint POST para crear una nueva solicitud de fondos
#     """
#     serializer = SolicitudFondosCreateSerializer(data=request.data)
    
#     if serializer.is_valid():
#         try:
#             solicitud = serializer.save()
#             return Response(
#                 {
#                     'success': True,
#                     'message': 'Solicitud de fondos creada exitosamente',
#                     'id': solicitud.id,
#                     'numero_formulario': solicitud.numeroFormulario
#                 },
#                 status=status.HTTP_201_CREATED
#             )
#         except Exception as e:
#             return Response(
#                 {
#                     'success': False,
#                     'message': f'Error al crear la solicitud: {str(e)}'
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
    
#     return Response(
#         {
#             'success': False,
#             'message': 'Datos inválidos',
#             'errors': serializer.errors
#         },
#         status=status.HTTP_400_BAD_REQUEST
#     )
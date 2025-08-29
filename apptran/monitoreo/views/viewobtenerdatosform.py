# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad
from spme_monitoreo.models import FormaPago
from ..serializers.serializerobtenerdatosform import (
    UsuarioSerializer, 
    ActividadSerializer, 
    ValidadorSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def obtener_datos_solicitud_fondos(request):
    """
    Endpoint POST para obtener datos necesarios para la solicitud de fondos
    """
    try:
        # print("=== INICIO DE REQUEST ===")
        # print("Request data:", request.data)
        
        # Validar datos de entrada
        id_actividad = request.data.get('id_actividad')
        username = request.data.get('usuario')
        
        if not id_actividad or not username:
            return Response(
                {
                    'success': False,
                    'message': 'Se requieren los campos id_actividad y usuario'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener usuario por username
        try:
            usuario = Usuario.objects.get(username=username)
            # print(f"Usuario encontrado: ID={usuario.id}, Username={usuario.username}")
            # print(f"Usuario datos: nombre='{usuario.nombre}', paterno='{usuario.paterno}', materno='{usuario.materno}'")
        except Usuario.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': f'Usuario con username {username} no encontrado'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener actividad
        try:
            actividad = Actividad.objects.get(id=id_actividad)
            # print(f"Actividad encontrada: ID={actividad.id}, Código={actividad.codigo}")
            # print(f"Actividad datos: descripcion='{actividad.descripcion}', fecha_inicio={actividad.fecha_inicio}, fecha_cierre={actividad.fecha_cierre}")
        except Actividad.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': f'Actividad con ID {id_actividad} no encontrada'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener validadores - todos los usuarios activos excepto el actual
        validadores = Usuario.objects.filter(is_active=True).exclude(id=usuario.id)
        
        #print(f"Validadores encontrados: {validadores.count()}")
        # for validador in validadores:
        #     print(f"  Validador: ID={validador.id}, Name='{validador.get_full_name()}'")
        #     print(f"    Datos: nombre='{validador.nombre}', paterno='{validador.paterno}', materno='{validador.materno}'")
        
        # Obtener formas de pago
        formas_pago = FormaPago.objects.all()
        formas_pago_list = [
             {
                'id': fp.id,
                'formaPago': fp.formaPago
            } 
            for fp in formas_pago if fp.formaPago
        ]
        #print(f"Formas de pago: {formas_pago_list}")
        
        # Serializar datos
        usuario_data = UsuarioSerializer(usuario).data
        #print(f"Usuario serializado: {usuario_data}")
        
        actividad_data = ActividadSerializer(actividad).data
        #print(f"Actividad serializada: {actividad_data}")
        
        validadores_data = ValidadorSerializer(validadores, many=True).data
        #print(f"Validadores serializados: {validadores_data}")
        
        response_data = {
            'usuario': usuario_data,
            'actividad': actividad_data,
            'validadores': validadores_data,
            'formaPago': formas_pago_list
        }
        
        #print("=== RESPONSE FINAL ===")
        #print("Response data:", response_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        #print(f"Error en obtener_datos_solicitud_fondos: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response(
            {
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
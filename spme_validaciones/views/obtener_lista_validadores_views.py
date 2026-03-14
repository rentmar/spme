#views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from spme_autenticacion.models import Usuario
from django.db.models import Q
from ..serializers.obtener_lista_validadores_serializers import UsuarioValidacionSerializers

class UsuarioValidacionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    #Metodo GET
    def get(self, request):
        #Serializar el usuario actual
        usuario_actual_serializer = UsuarioValidacionSerializers(request.user)

        #Obtener todos los usuarios activos excepto el actual
        otros_usuarios = Usuario.objects.filter(
            is_active = True
        ).exclude(
            Q(id=request.user.id) | Q(is_superuser=True) | Q(cargo='adminsis')
        ).order_by('nombre', 'paterno')

        #COntar el total de los validadores
        total_validadores = otros_usuarios.count()

        #Serializar los otros usuarios
        otros_usuarios_serializer = UsuarioValidacionSerializers(otros_usuarios, many=True)


        #Estructura de la respuesta
        response_data = {
            'success': True,
            'total_validadores': total_validadores,
            'usuarioActual': usuario_actual_serializer.data,
            'validadores': otros_usuarios_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

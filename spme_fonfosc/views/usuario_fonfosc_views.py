# spme/spme_fonfosc/views/usuario_fonfosc_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from spme_fonfosc.services.usuario_fonfosc_service import UsuarioFonFoscService
from ..models import Institucion

class VerificarUsernameView(APIView):
    """Vista para verificar disponibilidad de username"""

    def get(self, request):
        username = request.query_params.get('username', '').strip()

        if not username:
            return Response(
                {'detail': 'Parámetro username requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioFonFoscService.verificar_username(username)
        return Response(resultado, status=status.HTTP_200_OK)

class RegistroUsuarioFonFoscView(APIView):
    """Vista para registro de usuarios FONFOSC"""

    def post(self, request):
        try:
            datos = UsuarioFonFoscService.registrar_usuario(request.data)
            return Response(datos, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Institucion.DoesNotExist:
            return Response(
                {'detail': 'Institución no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
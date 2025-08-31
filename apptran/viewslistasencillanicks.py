# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from spme_autenticacion.models import Usuario

@api_view(['GET'])
def lista_nicks_usuarios(request):
    """
    Obtiene la lista de todos los usernames de usuarios.
    GET /usuarios/lista-nicks/
    """
    try:
        # Obtener todos los usernames de usuarios activos
        usernames = Usuario.objects.filter(is_active=True).values_list('username', flat=True)
        
        # Convertir a lista
        lista_nicks = list(usernames)
        
        return Response(lista_nicks)
        
    except Exception as e:
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
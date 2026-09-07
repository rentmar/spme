# spme/spme_gestion_acceso/views/usuario_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.usuarios.usuario_service import UsuarioService

class UsuarioSolicitanteView(APIView):
    
    def get(self, request, id_usuario):
        data = UsuarioService.obtener_solicitante(id_usuario)
        
        if not data:
            return Response(
                {'detail': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)
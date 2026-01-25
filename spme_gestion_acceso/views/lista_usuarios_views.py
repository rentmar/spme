#spme_gestion_acceso/views/lista_usuarios_views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from spme_autenticacion.models import Usuario
from ..serializers.lista_usuarios_serializer import UsuarioSerializer


class UsuarioListAPIView(generics.ListAPIView):
    serializer_class = UsuarioSerializer
    #permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filtra usuarios excluyendo superusuarios
        return Usuario.objects.filter(is_superuser=False)
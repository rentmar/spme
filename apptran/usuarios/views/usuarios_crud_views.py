from rest_framework import viewsets
from ..serializers.usuarios_crud_serializer import UsuarioCrudSerializer
from spme_autenticacion.models import Usuario

class UsuarioCrudView(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioCrudSerializer


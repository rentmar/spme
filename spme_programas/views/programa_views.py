from rest_framework import viewsets
from ..models import Programa
from ..serializers.programa_serializer import ProgramaSerializer

class ProgramaViewset(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
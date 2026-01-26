from rest_framework import viewsets
from spme_fonfosc.models import DepartamentoBolivia
from ..serializers.departamentos_bol_crud_basico_serializers import DepBoliviaSerializer

class DepBoliviaViews(viewsets.ModelViewSet):
    queryset = DepartamentoBolivia.objects.all()
    serializer_class = DepBoliviaSerializer
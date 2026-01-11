from rest_framework import viewsets
from spme_monitoreo.models import RendicionCuentasActPei
from ..serializers.rendicion_cuentas_pei_crud_serializer import RendicionCuentasActPeiSerializer


class RendicionCuentasActPeiView(viewsets.ModelViewSet):
    queryset = RendicionCuentasActPei.objects.all()
    serializer_class = RendicionCuentasActPeiSerializer

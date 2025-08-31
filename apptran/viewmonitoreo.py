from rest_framework import viewsets
from spme_monitoreo.models import FormaPago, SolicitudFondos, RendicionCuentas, SolicitudReembolso,SolicitudViaje, SolicitudPagoDirecto
from .serializermonitoreo import *


class FormaPagoView(viewsets.ModelViewSet):
    queryset = FormaPago.objects.all()
    serializer_class = FormPagoSer


class SolicitudFondosView(viewsets.ModelViewSet):
    queryset = SolicitudFondos.objects.all()
    serializer_class = SolicitudFondosSer

class RendicionCuentasView(viewsets.ModelViewSet):
    queryset = RendicionCuentas.objects.all()
    serializer_class = RendicionCuentasSer

class SolicitudReembolsoView(viewsets.ModelViewSet):
    queryset = SolicitudReembolso.objects.all()
    serializer_class = SolicitudReemboldoSer

class SolicitudViajeView(viewsets.ModelViewSet):
    queryset = SolicitudViaje.objects.all()
    serializer_class = SolicitudViajeSer

class SolicitudPagoDirectoView(viewsets.ModelViewSet):
    queryset = SolicitudPagoDirecto.objects.all()
    serializer_class = SolicitudPagoDirectoSer        
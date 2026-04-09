from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from spme_monitoreo.models import RendicionCuentas
from ..serializer.rendicion_cuentas_mas_solicitudes_serializer import RendicionConSolicitudesSerializer

class RendicionConSolicitudesDetailView(APIView):
    """
    GET /api/rendicion-con-solicitudes/<id>/
    Retorna la rendición de cuentas con todas sus solicitudes relacionadas
    """
    def get(self, request, pk):
        rendicion = get_object_or_404(
            RendicionCuentas.objects.select_related(
                'solicitudFondos',
                'solicitudReembolso',
                'solicitudViaje',
                'solicitudPagoDirecto',
                'usuario',
                'coordinador',
                'contador',
                'administrador',
                'actividad',
                'tarea',
            ),
            pk=pk
        )
        serializer = RendicionConSolicitudesSerializer(rendicion)
        return Response(serializer.data)
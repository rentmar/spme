from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from spme_estructuracion_proyecto.models import Proyecto
from ..serializers.estructura_proyecto_reportes_serializer import ProyectoDetailSerializer



class ProyectoEstructuraCompletaView(generics.RetrieveAPIView):
    """
    Endpoint que devuelve la estructura completa jerarquizada de un proyecto
    """
    queryset = Proyecto.objects.all().select_related(
        'objetivo_general'
    ).prefetch_related(
        'objetivo_general__resultados_og',
        'objetivo_general__objetivos_especificos_og',  # Solo objetivos específicos del OG
        'objetivo_general__objetivos_especificos_og__resultados_oe',
        'objetivo_general__objetivos_especificos_og__resultados_oe__productos_res_oe',
        'objetivo_general__objetivos_especificos_og__productos_oe',
        'actividad_proyecto'
    )
    serializer_class = ProyectoDetailSerializer
    lookup_field = 'id'

# Alternativa con función-based view
@api_view(['GET'])
def proyecto_estructura_completa(request, id):
    """
    Endpoint que devuelve la estructura completa jerarquizada de un proyecto
    """
    proyecto = get_object_or_404(
        Proyecto.objects.select_related('objetivo_general')
        .prefetch_related(
            'objetivo_general__resultados_og',
            'objetivo_general__objetivos_especificos_og',
            'objetivo_general__objetivos_especificos_og__resultados_oe',
            'objetivo_general__objetivos_especificos_og__resultados_oe__productos_res_oe',
            'objetivo_general__objetivos_especificos_og__productos_oe',
            'actividad_proyecto'
        ),
        id=id
    )
    serializer = ProyectoDetailSerializer(proyecto)
    return Response(serializer.data)
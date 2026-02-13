from rest_framework.decorators import api_view
from spme_estructuracion_proyecto.models import (
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjEspecifico
)

from ..serializers.obtener_indicadores_por_ids_serializer import (
    IndicadorObjetivoGeneralSerializer,
    IndicadorResultadoObjGralSerializer,
    IndicadorObjetivoEspecificoSerializer,
    IndicadorResultadoObjEspecificoSerializer
)

from ..utils.utils import procesar_consulta_indicadores

@api_view(['POST'])
def get_indicadores_og_by_ids(request):
    return procesar_consulta_indicadores(IndicadorObjetivoGeneral, IndicadorObjetivoGeneralSerializer, 'og', request)

@api_view(['POST'])
def get_indicadores_rog_by_ids(request):
    return procesar_consulta_indicadores(IndicadorResultadoObjGral, IndicadorResultadoObjGralSerializer, 'rog', request)

@api_view(['POST'])
def get_indicadores_oe_by_ids(request):
    return procesar_consulta_indicadores(IndicadorObjetivoEspecifico, IndicadorObjetivoEspecificoSerializer, 'oe', request)

@api_view(['POST'])
def get_indicadores_roe_by_ids(request):
    return procesar_consulta_indicadores(IndicadorResultadoObjEspecifico, IndicadorResultadoObjEspecificoSerializer, 'roe', request)
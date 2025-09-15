from rest_framework import serializers
from ..models import BitacoraIndicador
from spme_estructuracion_proyecto.models import (
    IndicadorProyecto, 
    IndicadorObjetivoGeneral, 
    IndicadorObjetivoEspecifico, 
    IndicadorResultadoObjGral, 
    IndicadorResultadoObjEspecifico
    )

class BitacoraIndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraIndicador
        fields = [
            'id',
            'fechaBitacora',
            'cantidadAvance',
            'reporteEscrito',
            'linkSubida',
            'tipoIndicador',
            'indicador'
        ]
        read_only_fields = ['id']
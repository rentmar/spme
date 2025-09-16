# serializers.py
from rest_framework import serializers
from spme_proyectos_reportes.models import BitacoraIndicador

class BitacoraIndicadorSerializer(serializers.ModelSerializer):
    # Campos para mostrar información relacionada en lugar de solo IDs
    indicadorog_codigo = serializers.CharField(source='indicadorog.codigo', read_only=True)
    indicadoroe_codigo = serializers.CharField(source='indicadoroe.codigo', read_only=True)
    indicadorrog_codigo = serializers.CharField(source='indicadorrog.codigo', read_only=True)
    indicadorroe_codigo = serializers.CharField(source='indicadorroe.codigo', read_only=True)
    
    class Meta:
        model = BitacoraIndicador
        fields = [
            'id',
            'fechaBitacora',
            'cantidadAvance',
            'reporteEscrito',
            'linkSubida',
            'tipoIndicador',
            'indicadorog',
            'indicadoroe',
            'indicadorrog',
            'indicadorroe',
            'indicadorog_codigo',
            'indicadoroe_codigo',
            'indicadorrog_codigo',
            'indicadorroe_codigo'
        ]
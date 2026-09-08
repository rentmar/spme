# spme/spme_fonfosc/serializers/institucion_crud_basico_serializer.py

from rest_framework import serializers

from spme_fonfosc.models import Institucion
from spme_fonfosc.serializers.departamentos_bol_crud_basico_serializers import DepBoliviaSerializer


class InstitucionSerializer(serializers.ModelSerializer):
    """Serializer para listar instituciones con toda su información"""

    departamentoSede = DepBoliviaSerializer(read_only=True)
    departamentoIntervencion = DepBoliviaSerializer(many=True, read_only=True)

    class Meta:
        model = Institucion
        fields = [
            'id',
            'sigla',
            'nombre',
            'emailInstitucion',
            'telefono',
            'direccion',
            'ciudad',
            'departamentoSede',
            'casillaPostal',
            'webSite',
            'departamentoIntervencion',
        ]
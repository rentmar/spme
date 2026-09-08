# spme/spme_fonfosc/serializers/institucion_crud_basico_serializer.py
from rest_framework import serializers

from spme_fonfosc.models import Institucion


class InstitucionSerializer(serializers.ModelSerializer):
    """Serializer para listar instituciones"""

    departamento = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Institucion
        fields = [
            'id',
            'nombre',
            'sigla',
            'emailInstitucion',
            'telefono',
            'direccion',
            'casillaPostal',
            'webSite',
            'departamento',
        ]
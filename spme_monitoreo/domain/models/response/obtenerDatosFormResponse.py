from rest_framework import serializers
from spme_autenticacion.domain.models.response.userResponse import UsuarioResponse,UsuarioValidadorResponse

class ObtenerDatosFormularioResponse(serializers.Serializer):
    usuario = UsuarioResponse(required=False)
    actividad = serializers.JSONField(required=False)
    validadores = UsuarioValidadorResponse(many=True, required=False)
    formaPago = serializers.ListField(child=serializers.CharField(), required=False)
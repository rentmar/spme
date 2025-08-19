from rest_framework import serializers
from spme_autenticacion.domain.models.response.userResponse import UsuarioResponse,UsuarioValidadorResponse
from spme_actividades.domain.models.response.actividadesResponse import ObtenerDatosFormActividadResponse
class ObtenerDatosFormularioResponse(serializers.Serializer):
    usuario = UsuarioResponse(required=False)
    actividad = ObtenerDatosFormActividadResponse(required=False)
    validadores = UsuarioValidadorResponse(many=True, required=False)
    formaPago = serializers.ListField(child=serializers.CharField(), required=False)
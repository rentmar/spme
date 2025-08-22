from rest_framework import serializers

class ObtenerDatosFormularioRequest(serializers.Serializer):
    id_actividad = serializers.IntegerField(required=True)
    usuario = serializers.CharField(required=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id": internal_value.get("id_actividad"),
            "username": internal_value.get("usuario"),
        }

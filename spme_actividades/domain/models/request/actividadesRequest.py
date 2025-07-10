from rest_framework import serializers

class ObtenerActividadesUsuarioRequest(serializers.Serializer):
    user_id = serializers.IntegerField()

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'user_id': int(internal_value['user_id']),
        }
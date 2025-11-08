from rest_framework import serializers

class ObtenerFormaPagoRequest(serializers.Serializer):
    """
    Request para obtener formas de pago
    """
    # Puedes agregar filtros aquí si los necesitas en el futuro
    id_formaPago = serializers.IntegerField(required=False, allow_null=True)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            "id_formaPago": internal_value.get("id_formaPago"),
        }
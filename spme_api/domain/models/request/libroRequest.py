from rest_framework import serializers

class LibroRequest(serializers.Serializer):
    codigo_libro = serializers.IntegerField(max_value=99999)

    def to_internal_value(self, data):
        # Esto maneja el mapeo durante la deserialización (entrada)
        internal_value = super().to_internal_value(data)
        return {'codigo': internal_value['codigo_libro']}





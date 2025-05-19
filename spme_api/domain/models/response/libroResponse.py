from rest_framework import serializers

class LibroResponse(serializers.Serializer):
    titulo = serializers.CharField()
    disponible = serializers.BooleanField()
    
    def to_representation(self, instance):
        # Convierte codigo a codigo_libro en la salida
        data = super().to_representation(instance)
        data['titulo_libro'] = data.pop('titulo')
        data['disponible_libro'] = data.pop('disponible')
        return data
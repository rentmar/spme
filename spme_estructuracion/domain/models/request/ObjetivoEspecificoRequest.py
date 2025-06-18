from rest_framework import serializers

class ObjetivoEspecificoRequest(serializers.Serializer):
    codigo_objetivoEspecifico = serializers.IntegerField(max_value=99999)   #codigo recibido no debe ecceder de 99999

    def to_internal_value(self, data):
        # Esto maneja el mapeo durante la deserialización (entrada)
        internal_value = super().to_internal_value(data)
        #print(internal_value) #{'codigo_libro': 123}
        return {'codigo': internal_value['codigo_objetivoEspecifico']}       

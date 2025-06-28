from rest_framework import serializers

class GetUserRequest(serializers.Serializer):
    """
    Usuario request user_name requerido.
    """
    usuario = serializers.CharField(max_length=150, required=True, allow_blank=False) 

    def to_internal_value(self, data):
        """
        campo user_name se convierte a usuario.
        """
        internal_value = super().to_internal_value(data)
        return {'usuario': internal_value['usuario']} 
    
class CreateUserRequest(serializers.Serializer):
    """
    Usuario request para crear un usuario.
    """
    usuario = serializers.CharField(max_length=150, required=True, allow_blank=False)
    password = serializers.CharField(max_length=128, required=True, allow_blank=False)
    permisos = serializers.CharField(max_length=10, required=True, allow_blank=False)
    def to_internal_value(self, data):
        """
        Convierte los campos a un formato DB.
        """
        internal_value = super().to_internal_value(data)
        return {
            'usuario': internal_value['usuario'],
            'password': internal_value['password'],
            'permisos': internal_value['permisos']
        }
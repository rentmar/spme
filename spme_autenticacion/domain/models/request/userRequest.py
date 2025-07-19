from rest_framework import serializers

class ObtenerUsuarioRequest(serializers.Serializer):
    """
    Usuario request user_name requerido.
    """
    usuario = serializers.CharField(max_length=150, required=True, allow_blank=False) 

    def to_internal_value(self, data):
        """
        campo user_name se convierte a usuario.
        """
        internal_value = super().to_internal_value(data)
        return {'username': internal_value['usuario']} 
    
class CrearUsuarioRequest(serializers.Serializer):
    """
    Usuario request para crear un usuario.
    """
    usuario = serializers.CharField(max_length=150, required=True, allow_blank=False)
    nombre = serializers.CharField(max_length=150, required=True, allow_blank=False)
    paterno = serializers.CharField(max_length=150, required=True, allow_blank=False)
    materno = serializers.CharField(max_length=150, required=True, allow_blank=False)
    password = serializers.CharField(max_length=128, required=True, allow_blank=False)
    permisos = serializers.CharField(max_length=10, required=True, allow_blank=False)
    activo = serializers.BooleanField(default=True)
    staff = serializers.BooleanField(default=False)
    
    def to_internal_value(self, data):
        """
        Convierte los campos a un formato DB.
        """
        internal_value = super().to_internal_value(data)
        return {
            'username': internal_value['usuario'],
            'nombre': internal_value['nombre'],
            'paterno': internal_value['paterno'],
            'materno': internal_value['materno'],
            'password': internal_value['password'],
            'permisos': internal_value['permisos'],
            'is_active': internal_value['activo'],
            'is_staff': internal_value['staff']
        }
    
class AutenticacionUsuarioRequest(serializers.Serializer):
    """
    Request para autenticar un usuario.
    """
    usuario = serializers.CharField(max_length=50, required=True, allow_blank=False)
    password = serializers.CharField(max_length=150, required=True, allow_blank=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'username': internal_value['usuario'],
            'password': internal_value['password']
        }
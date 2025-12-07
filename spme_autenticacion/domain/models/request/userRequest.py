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

class UsuarioRequest(serializers.Serializer):
    """
    Usuario request para crear un usuario.
    """
    usuario = serializers.CharField(max_length=150, required=True, allow_blank=False)
    nombre = serializers.CharField(max_length=150, required=True, allow_blank=False)
    paterno = serializers.CharField(max_length=150, required=True, allow_blank=False)
    materno = serializers.CharField(max_length=150, required=True, allow_blank=False)
    correo = serializers.CharField(max_length=150, required=False, allow_blank=True)
    ci = serializers.CharField(max_length=15, required=True, allow_blank=False)
    cargo = serializers.CharField(max_length=50, required=True, allow_blank=False)
    banco = serializers.CharField(max_length=100, required=True, allow_blank=False)
    numero_cuenta = serializers.CharField(max_length=150, required=True, allow_blank=False)
    tipo_cuenta = serializers.CharField(max_length=25, required=True, allow_blank=False)
    permisos = serializers.CharField(max_length=10, required=True, allow_blank=False)
    activo = serializers.BooleanField(default=True)
    
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
            'correo': internal_value['correo'],
            'ci': internal_value['ci'],
            'cargo': internal_value['cargo'],
            'banco': internal_value['banco'],
            'numero_cuenta': internal_value['numero_cuenta'],
            'tipo_cuenta': internal_value['tipo_cuenta'],
            'permisos': internal_value['permisos'],
            'is_active': internal_value['activo'],
            'is_staff': True,
            'is_superuser': False
        }

class CrearUsuarioRequest(UsuarioRequest):
    password = serializers.CharField(max_length=128, required=True, allow_blank=False)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        internal_value['password'] = data['password']
        return internal_value

class ActualizarUsuarioRequest(serializers.Serializer):
    id_usuario = serializers.IntegerField(required=True)
    usuario = serializers.CharField(max_length=150, required=False, allow_blank=True)
    nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    paterno = serializers.CharField(max_length=150, required=False, allow_blank=True)
    materno = serializers.CharField(max_length=150, required=False, allow_blank=True)
    correo = serializers.CharField(max_length=150, required=False, allow_blank=True)
    ci = serializers.CharField(max_length=15, required=False, allow_blank=True)
    cargo = serializers.CharField(max_length=50, required=False, allow_blank=True)
    banco = serializers.CharField(max_length=100, required=False, allow_blank=True)
    numero_cuenta = serializers.CharField(max_length=150, required=False, allow_blank=True)
    tipo_cuenta = serializers.CharField(max_length=25, required=False, allow_blank=True)
    permisos = serializers.CharField(max_length=10, required=False, allow_blank=True)
    activo = serializers.BooleanField(required=False)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        mapped_data = {
            'id': internal_value['id_usuario'],
            'username': internal_value.get('usuario'),
            'nombre': internal_value.get('nombre'),
            'paterno': internal_value.get('paterno'),
            'materno': internal_value.get('materno'),
            'correo': internal_value.get('correo'),
            'ci': internal_value.get('ci'),
            'cargo': internal_value.get('cargo'),
            'banco': internal_value.get('banco'),
            'numero_cuenta': internal_value.get('numero_cuenta'),
            'tipo_cuenta': internal_value.get('tipo_cuenta'),
            'permisos': internal_value.get('permisos'),
            'is_active': internal_value.get('activo'),
        }
        # Devuelve solo los campos que fueron enviados en la petición (no None)
        return {key: value for key, value in mapped_data.items() if value is not None}

class CambioEstadoUsuarioRequest(serializers.Serializer):
    """
    Usuario request para desactivar un usuario.
    """
    id_usuario = serializers.IntegerField(required=True)
    activo = serializers.BooleanField(default=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato DB.
        """
        internal_value = super().to_internal_value(data)
        return {
            'id': internal_value['id_usuario'],
            'is_active': internal_value['activo']
        }

class CambioPasswordUsuarioRequest(serializers.Serializer):
    """
    Usuario request para reset password un usuario.
    """
    id_usuario = serializers.IntegerField(required=True)
    password = serializers.CharField(max_length=128, required=True, allow_blank=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato DB.
        """
        internal_value = super().to_internal_value(data)
        return {
            'id': internal_value['id_usuario'],
            'password': internal_value['password']
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
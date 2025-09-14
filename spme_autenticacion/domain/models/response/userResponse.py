from rest_framework import serializers

class UsuarioValidadorResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=150)
    paterno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    materno = serializers.CharField(required=False, allow_blank=True, max_length=150)
    cargo = serializers.CharField(required=False,allow_blank=True, max_length=50)
  
class UsuarioResponse(UsuarioValidadorResponse):
    usuario = serializers.CharField(required=False, allow_blank=True, max_length=150)
    ci = serializers.CharField(required=False,allow_blank=True, max_length=12)
    banco = serializers.CharField(required=False,allow_blank=True, max_length=50)
    numero_cuenta = serializers.CharField(required=False,allow_blank=True, max_length=50)
    tipo_cuenta = serializers.CharField(required=False,allow_blank=True, max_length=20)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=20)
    es_activo = serializers.BooleanField(required=False)
    
class CreateUserResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class ActualizarUsuarioResponse(serializers.Serializer):
    usuario = serializers.CharField(required=False, allow_blank=True, max_length=150)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)

class AutenticacionUsuarioResponse(serializers.Serializer):
    validacion = serializers.BooleanField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
    usuario = serializers.CharField(required=False, allow_blank=False, max_length=150)
    rol = serializers.CharField(required=False, allow_blank=True, max_length=20)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=20)
    # token = serializers.CharField(required=False, allow_blank=True, max_length=200)
    # refresh_token = serializers.CharField(required=False, allow_blank=True, max_length=200)

class ListaUsuariosResponse(serializers.Serializer):
    usuarios = UsuarioResponse(many=True)

class ListaValidadoresResponse(serializers.Serializer):
    validadores = UsuarioValidadorResponse(many=True)

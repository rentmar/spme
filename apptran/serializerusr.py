from rest_framework import serializers
from rest_framework import generics, status
from django.contrib.auth.password_validation import validate_password
from spme_autenticacion.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuatiosNicksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username']        


class RegistrarSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ('username', 'password', 'password2', 'nombre', 'paterno', 
                 'materno', 'ci', 'cargo', 'banco', 'numero_cuenta', 
                 'tipo_cuenta', 'permisos')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Usuario.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])




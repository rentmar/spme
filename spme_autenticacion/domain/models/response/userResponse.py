from rest_framework import serializers

class UserResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    usuario = serializers.CharField(required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(required=False, allow_blank=True, max_length=30)
    permisos = serializers.CharField(required=False, allow_blank=True, max_length=150)

class CreateUserResponse(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    mensaje = serializers.CharField(required=False, allow_blank=True, max_length=150)
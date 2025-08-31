from rest_framework import serializers
from .models import SystemConfig
from django.contrib.auth import get_user_model

User = get_user_model()

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = "__all__"
        read_only_fields = ('initialized', 'initialized_at', 'created_at', 'updated_at')
        #read_only_fields = ('inizializado', 'inizializado_el', 'created_at', 'updated_at')


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirmation')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        return User.objects.create_superuser(**validated_data)


class SetupStatusSerializer(serializers.Serializer):
    needs_setup = serializers.BooleanField()
    database_ready = serializers.BooleanField()
    admin_exists = serializers.BooleanField()
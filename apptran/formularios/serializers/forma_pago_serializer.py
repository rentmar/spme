# serializers/forma_pago_serializer.py

from rest_framework import serializers


class BeneficiarioSerializer(serializers.Serializer):
    ci = serializers.CharField()
    nombre = serializers.CharField()
    banco = serializers.CharField(required=False, allow_blank=True)
    tipo_cuenta = serializers.CharField(required=False, allow_blank=True)
    numero_cuenta = serializers.CharField(required=False, allow_blank=True)


class BeneficiariosAgrupadosSerializer(serializers.Serializer):
    efectivo = BeneficiarioSerializer(many=True)
    transferencia = BeneficiarioSerializer(many=True)
    cheque = BeneficiarioSerializer(many=True)
    todos = BeneficiarioSerializer(many=True)
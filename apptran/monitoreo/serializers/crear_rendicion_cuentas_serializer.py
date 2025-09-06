# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentas

class RendicionCuentasSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentas
        fields = [
            'id',
            'numeroFormulario',
            'cpteDiario',
            'fechaDesembolso',
            'montoAsignado',
            'montoDescargado',
            'saldo',
            'detalleDestinoFondos',
            'validacionResponsable',
            'responsable',
            'validacionCoordinador',
            'coordinador',
            'validacionContador',
            'contador',
            'validacionAdministrador',
            'administrador',
            'usuario',
            'solicitudFondos',
            'SolicitudReembolso',
            'solicitudViaje',
            'solicitudPagoDirecto'
        ]
        read_only_fields = ['id']  # El saldo podría calcularse automáticamente

    def create(self, validated_data):
        # Calculamos el saldo automáticamente si se proporcionan montos
        monto_asignado = validated_data.get('montoAsignado', 0) or 0
        monto_descargado = validated_data.get('montoDescargado', 0) or 0
        
        if monto_asignado is not None and monto_descargado is not None:
            validated_data['saldo'] = monto_asignado - monto_descargado
        
        return super().create(validated_data)
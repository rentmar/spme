from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentas
from spme_autenticacion.models import Usuario

class RendicionCuentasSerializer(serializers.ModelSerializer):
    usuario_info = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    
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
            'actividad',
            'fechaActividad',
            'fechaRendicion',
            'descripcionActividad',
            'lugarActividad',
            'lugarRendicion',
            'tarea',
            'bloquearIconos',
            'usuario_info',
            'validacionResponsable',
            'validacionCoordinador',
            'validacionContador',
            'validacionAdministrador',
            'estado_validacion',
            'solicitudFondos',
            'solicitudReembolso',
            'solicitudViaje',
            'solicitudPagoDirecto'
        ]
    
    def get_usuario_info(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo
            }
        return None
    
    def get_estado_validacion(self, obj):
        if (obj.validacionResponsable and obj.validacionCoordinador and 
            obj.validacionContador and obj.validacionAdministrador):
            return 'validado_completamente'
        elif obj.validacionResponsable or obj.validacionCoordinador or obj.validacionContador or obj.validacionAdministrador:
            return 'validado_parcialmente'
        else:
            return 'pendiente'
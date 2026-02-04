# serializers.py (en la misma carpeta)
from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentas
from spme_autenticacion.models import Usuario

class RendicionCuentasSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar rendiciones de cuentas"""
    
    # Información del usuario que creó la rendición
    usuario_info = serializers.SerializerMethodField()
    # Información de validaciones
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
            return 'validada_completamente'
        elif (obj.validacionResponsable or obj.validacionCoordinador or 
              obj.validacionContador or obj.validacionAdministrador):
            return 'validada_parcialmente'
        else:
            return 'pendiente'
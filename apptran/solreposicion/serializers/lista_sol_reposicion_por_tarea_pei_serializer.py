from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolsoActPei

class SolicitudReembolsoActPeiSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    responsable_nombre = serializers.SerializerMethodField()
    coordinador_nombre = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    actividad_nombre = serializers.SerializerMethodField()
    tarea_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudReembolsoActPei
        fields = [
            'id',
            'numeroFormulario',
            'detalleDestinoFondos',
            'formaPago',
            'forma_pago_nombre',
            'lugarSolicitud',
            'fechaSolicitud',
            'fechaRealizacionActividad',
            'montoSolicitado',
            'descripcion_actividad',
            'objetivo_actividad',
            'datos_forma_pago',
            'solicitante',
            'responsable_nombre',
            'coordinador_nombre',
            'actividad_nombre',
            'tarea_nombre',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'bloquearIconos',
            'actividad',
            'tarea',
            'usuario',
            'responsable',
            'coordinador'
        ]
    
    def get_solicitante(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo if hasattr(obj.usuario, 'cargo') else None
            }
        return None
    
    def get_responsable_nombre(self, obj):
        if obj.responsable:
            return obj.responsable.get_full_name()
        return None
    
    def get_coordinador_nombre(self, obj):
        if obj.coordinador:
            return obj.coordinador.get_full_name()
        return None
    
    def get_actividad_nombre(self, obj):
        if obj.actividad and hasattr(obj.actividad, 'nombreCorto'):
            return obj.actividad.nombreCorto
        return None
    
    def get_tarea_nombre(self, obj):
        if obj.tarea and hasattr(obj.tarea, 'titulo'):
            return obj.tarea.titulo
        return None
    
    def get_forma_pago_nombre(self, obj):
        if obj.formaPago and hasattr(obj.formaPago, 'formaPago'):
            return obj.formaPago.formaPago
        return None
    
    def get_estado_validacion(self, obj):
        if obj.validacionResponsable and obj.validacionCoordinador:
            return 'validado_completamente'
        elif obj.validacionResponsable:
            return 'validado_parcialmente'
        elif obj.validacionCoordinador:
            return 'rechazado'
        else:
            return 'pendiente'
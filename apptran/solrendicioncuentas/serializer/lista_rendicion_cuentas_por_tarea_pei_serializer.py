from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentasActPei

class RendicionCuentasActPeiSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    responsable_nombre = serializers.SerializerMethodField()
    coordinador_nombre = serializers.SerializerMethodField()
    contador_nombre = serializers.SerializerMethodField()
    administrador_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    actividad_nombre = serializers.SerializerMethodField()
    tarea_nombre = serializers.SerializerMethodField()
    solicitud_fondos_info = serializers.SerializerMethodField()
    solicitud_reembolso_info = serializers.SerializerMethodField()
    solicitud_viaje_info = serializers.SerializerMethodField()
    solicitud_pago_directo_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RendicionCuentasActPei
        fields = [
            'id',
            'numeroFormulario',
            'cpteDiario',
            'fechaDesembolso',
            'fechaActividad',
            'fechaRendicion',
            'montoAsignado',
            'montoDescargado',
            'saldo',
            'detalleDestinoFondos',
            'descripcionActividad',
            'lugarActividad',
            'lugarRendicion',
            'solicitante',
            'responsable_nombre',
            'coordinador_nombre',
            'contador_nombre',
            'administrador_nombre',
            'estado_validacion',
            'actividad_nombre',
            'tarea_nombre',
            'solicitud_fondos_info',
            'solicitud_reembolso_info',
            'solicitud_viaje_info',
            'solicitud_pago_directo_info',
            'validacionResponsable',
            'validacionCoordinador',
            'validacionContador',
            'validacionAdministrador',
            'bloquearIconos',
            'actividad',
            'tarea',
            'usuario',
            'responsable',
            'coordinador',
            'contador',
            'administrador',
            'solicitudFondos',
            'solicitudReembolso',
            'solicitudViaje',
            'solicitudPagoDirecto'
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
    
    def get_contador_nombre(self, obj):
        if obj.contador:
            return obj.contador.get_full_name()
        return None
    
    def get_administrador_nombre(self, obj):
        if obj.administrador:
            return obj.administrador.get_full_name()
        return None
    
    def get_actividad_nombre(self, obj):
        if obj.actividad and hasattr(obj.actividad, 'nombreCorto'):
            return obj.actividad.nombreCorto
        return None
    
    def get_tarea_nombre(self, obj):
        if obj.tarea and hasattr(obj.tarea, 'titulo'):
            return obj.tarea.titulo
        return None
    
    def get_solicitud_fondos_info(self, obj):
        if obj.solicitudFondos:
            return {
                'id': obj.solicitudFondos.id,
                'numeroFormulario': obj.solicitudFondos.numeroFormulario,
                'montoSolicitado': obj.solicitudFondos.montoSolicitado
            }
        return None
    
    def get_solicitud_reembolso_info(self, obj):
        if obj.solicitudReembolso:
            return {
                'id': obj.solicitudReembolso.id,
                'numeroFormulario': obj.solicitudReembolso.numeroFormulario,
                'montoSolicitado': obj.solicitudReembolso.montoSolicitado
            }
        return None
    
    def get_solicitud_viaje_info(self, obj):
        if obj.solicitudViaje:
            return {
                'id': obj.solicitudViaje.id,
                'numeroFormulario': obj.solicitudViaje.numeroFormulario,
                'montoSolicitado': obj.solicitudViaje.montoSolicitado
            }
        return None
    
    def get_solicitud_pago_directo_info(self, obj):
        if obj.solicitudPagoDirecto:
            return {
                'id': obj.solicitudPagoDirecto.id,
                'numeroFormulario': obj.solicitudPagoDirecto.numeroFormulario,
                'montoSolicitado': obj.solicitudPagoDirecto.montoSolicitado
            }
        return None
    
    def get_estado_validacion(self, obj):
        validaciones = [
            obj.validacionResponsable,
            obj.validacionCoordinador,
            obj.validacionContador,
            obj.validacionAdministrador
        ]
        
        total = len(validaciones)
        aprobadas = sum(validaciones)
        
        if aprobadas == total:
            return 'validado_completamente'
        elif aprobadas > 0:
            return 'validado_parcialmente'
        else:
            return 'pendiente'
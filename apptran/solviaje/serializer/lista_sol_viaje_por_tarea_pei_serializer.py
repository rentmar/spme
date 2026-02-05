from rest_framework import serializers
from spme_monitoreo.models import SolicitudViajeActPei

class SolicitudViajeActPeiSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    responsable_nombre = serializers.SerializerMethodField()
    coordinador_nombre = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    actividad_nombre = serializers.SerializerMethodField()
    tarea_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudViajeActPei
        fields = [
            'id',
            'numeroFormulario',
            'evento',
            'lugarEvento',
            'fechaEvento',
            'institucionesParticipantes',
            'organizador',
            'quienCubreGastos',
            'justificacionAsistencia',
            'fondosUnitas',
            'tareasPrevias',
            'detalleGasto',
            'formaPago',
            'forma_pago_nombre',
            'montoSolicitado',
            'lugarSolicitud',
            'fechaSolicitud',
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
            'tarea',  # Aquí está el campo "tarea" sin "Tarea" en el nombre
            'usuario',
            'responsable',
            'coordinador'
        ]
        read_only_fields = ['numeroFormulario']
    
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
        if obj.actividad:
            if hasattr(obj.actividad, 'nombreCorto'):
                return obj.actividad.nombreCorto
            elif hasattr(obj.actividad, 'nombre'):
                return obj.actividad.nombre
            elif hasattr(obj.actividad, 'descripcion'):
                return obj.actividad.descripcion[:50] + '...' if len(obj.actividad.descripcion) > 50 else obj.actividad.descripcion
        return None
    
    def get_tarea_nombre(self, obj):
        if obj.tarea:
            if hasattr(obj.tarea, 'titulo'):
                return obj.tarea.titulo
            elif hasattr(obj.tarea, 'nombre'):
                return obj.tarea.nombre
            elif hasattr(obj.tarea, 'descripcion'):
                return obj.tarea.descripcion[:50] + '...' if len(obj.tarea.descripcion) > 50 else obj.tarea.descripcion
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
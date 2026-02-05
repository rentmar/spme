from rest_framework import serializers
from spme_actividades.models import ActividadPei, TareaActividadPei
from spme_autenticacion.models import Usuario
from spme_monitoreo.models import SolicitudFondosActPei, FormaPago


class SolicitudFondosActPeiSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    contador_nombre = serializers.SerializerMethodField()
    coordinador_nombre = serializers.SerializerMethodField()
    actividad_nombre = serializers.SerializerMethodField()
    tarea_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudFondosActPei
        fields = [
            'id',
            'numeroFormulario',
            'fechaSolicitud',
            'fechaRealizacionActividad',
            'montoSolicitado',
            'detalleDestinoFondos',
            'formaPago',
            'forma_pago_nombre',
            'lugarSolicitud',
            'descripcion_actividad',
            'objetivo_actividad',
            'datos_forma_pago',
            'solicitante',
            'contador_nombre',
            'coordinador_nombre',
            'actividad_nombre',
            'tarea_nombre',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'bloquearIconosSolFondos',
            'actividad',
            'tarea',
            'usuario',
            'contador',
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
    
    def get_contador_nombre(self, obj):
        if obj.contador:
            return obj.contador.get_full_name()
        return None
    
    def get_coordinador_nombre(self, obj):
        if obj.coordinador:
            return obj.coordinador.get_full_name()
        return None
    
    def get_actividad_nombre(self, obj):
        if obj.actividad:
            # Usar el campo correcto del modelo ActividadPei
            if hasattr(obj.actividad, 'nombre'):
                return obj.actividad.nombre
            elif hasattr(obj.actividad, 'nombreCorto'):
                return obj.actividad.nombreCorto
            elif hasattr(obj.actividad, 'descripcion'):
                return obj.actividad.descripcion[:50] + '...' if len(obj.actividad.descripcion) > 50 else obj.actividad.descripcion
        return None
    
    def get_tarea_nombre(self, obj):
        if obj.tarea:
            # Usar el campo correcto del modelo TareaActividadPei
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
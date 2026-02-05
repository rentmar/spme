 # serializers.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolsoActPei, FormaPago
from spme_autenticacion.models import Usuario


class SolicitudReembolsoActPeiSerializer(serializers.ModelSerializer):
    """Serializador para solicitudes de reembolso Actividad Pei"""
    
    # Información del usuario que creó la solicitud
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    estado_validacion_display = serializers.SerializerMethodField()
    # Nombre de la forma de pago
    forma_pago_nombre = serializers.SerializerMethodField()
    # Información del responsable
    responsable_info = serializers.SerializerMethodField()
    # Información del coordinador
    coordinador_info = serializers.SerializerMethodField()
    # Información de la actividad PEI
    actividad_pei_info = serializers.SerializerMethodField()
    # Información de la tarea PEI
    tarea_pei_info = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudReembolsoActPei
        fields = [
            'id',
            'numeroFormulario',
            'fechaSolicitud',
            'montoSolicitado',
            'descripcion_actividad',
            'objetivo_actividad',
            'lugarSolicitud',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'estado_validacion_display',
            'formaPago',
            'forma_pago_nombre',
            'responsable_info',
            'coordinador_info',
            'fechaRealizacionActividad',
            'bloquearIconos',
            'actividad',
            'tarea',
            'actividad_pei_info',
            'tarea_pei_info',
            'detalleDestinoFondos',
            'datos_forma_pago'
        ]
    
    def get_solicitante(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo
            }
        return None
    
    def get_estado_validacion(self, obj):
        if obj.validacionResponsable and obj.validacionCoordinador:
            return 'completamente_validada'
        elif obj.validacionResponsable and not obj.validacionCoordinador:
            return 'parcialmente_validada'
        elif not obj.validacionResponsable and obj.validacionCoordinador:
            return 'validacion_inversa'
        else:
            return 'pendiente'
    
    def get_estado_validacion_display(self, obj):
        estado = self.get_estado_validacion(obj)
        estados = {
            'completamente_validada': 'Validada Completamente',
            'parcialmente_validada': 'Validada Parcialmente',
            'validacion_inversa': 'Validación Inversa',
            'pendiente': 'Pendiente'
        }
        return estados.get(estado, estado)
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'
    
    def get_responsable_info(self, obj):
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'nombre_completo': obj.responsable.get_full_name(),
                'cargo': obj.responsable.cargo
            }
        return None
    
    def get_coordinador_info(self, obj):
        if obj.coordinador:
            return {
                'id': obj.coordinador.id,
                'nombre_completo': obj.coordinador.get_full_name(),
                'cargo': obj.coordinador.cargo
            }
        return None
    
    def get_actividad_pei_info(self, obj):
        if obj.actividad:
            return {
                'id': obj.actividad.id,
                'codigo': obj.actividad.codigo,
                'nombre_corto': obj.actividad.nombreCorto,
                'descripcion': obj.actividad.descripcion,
                'estado': obj.actividad.estado,
                'estado_display': obj.actividad.get_estado_display(),
                'fecha_inicio': obj.actividad.fecha_inicio,
                'fecha_cierre': obj.actividad.fecha_cierre,
                'presupuesto': float(obj.actividad.presupuesto) if obj.actividad.presupuesto else 0,
                'responsable_id': obj.actividad.responsable.id if obj.actividad.responsable else None,
                'responsable_nombre': obj.actividad.responsable.get_full_name() if obj.actividad.responsable else None
            }
        return None
    
    def get_tarea_pei_info(self, obj):
        if obj.tarea:
            return {
                'id': obj.tarea.id,
                'codigo': obj.tarea.codigo,
                'titulo': obj.tarea.titulo,
                'descripcion': obj.tarea.descripcion,
                'estado': obj.tarea.estado,
                'estado_display': obj.tarea.get_estado_display(),
                'fecha_ejecucion': obj.tarea.fecha_ejecucion,
                'fecha_limite': obj.tarea.fecha_limite,
                'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0
            }
        return None
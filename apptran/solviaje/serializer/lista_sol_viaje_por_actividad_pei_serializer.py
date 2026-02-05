# lista_sol_viaje_por_actividad_pei_serializer.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudViajeActPei, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import ActividadPei, TareaActividadPei


class SolicitudViajeActPeiSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar solicitudes de viaje de ActividadPei"""
    
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
            'bloquearIconos',
            'formaPago',
            'forma_pago_nombre',
            'montoSolicitado',
            'lugarSolicitud',
            'fechaSolicitud',
            'detalleGasto',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'estado_validacion_display',
            'responsable_info',
            'coordinador_info',
            'actividad',
            'tarea',
            'actividad_pei_info',
            'tarea_pei_info',
            'datos_forma_pago'
        ]
        read_only_fields = ['numeroFormulario']
    
    def get_solicitante(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'nombre_completo': obj.usuario.get_full_name(),
                'cargo': obj.usuario.cargo
            }
        return None
    
    def get_estado_validacion(self, obj):
        """Retorna el estado de validación en formato texto"""
        if obj.validacionResponsable and obj.validacionCoordinador:
            return 'validada_completamente'
        elif obj.validacionResponsable and not obj.validacionCoordinador:
            return 'validada_parcialmente'
        elif not obj.validacionResponsable and obj.validacionCoordinador:
            return 'rechazada'  # Coordinador rechazó
        else:
            return 'pendiente'
    
    def get_estado_validacion_display(self, obj):
        """Retorna el estado de validación en formato legible"""
        estados = {
            'validada_completamente': 'Validada Completamente',
            'validada_parcialmente': 'Validada Parcialmente',
            'rechazada': 'Rechazada',
            'pendiente': 'Pendiente'
        }
        estado = self.get_estado_validacion(obj)
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
        """Obtiene información de la ActividadPei relacionada"""
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
        """Obtiene información de la TareaActividadPei relacionada"""
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
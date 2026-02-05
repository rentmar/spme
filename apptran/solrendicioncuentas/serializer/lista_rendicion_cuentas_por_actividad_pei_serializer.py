# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import RendicionCuentasActPei
from spme_autenticacion.models import Usuario


class RendicionCuentasActPeiSerializer(serializers.ModelSerializer):
    """Serializador para rendiciones de cuentas Actividad Pei"""
    
    # Información del usuario que creó la rendición
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    estado_validacion_display = serializers.SerializerMethodField()
    # Información del responsable
    responsable_info = serializers.SerializerMethodField()
    # Información del coordinador
    coordinador_info = serializers.SerializerMethodField()
    # Información del contador
    contador_info = serializers.SerializerMethodField()
    # Información del administrador
    administrador_info = serializers.SerializerMethodField()
    # Información de la actividad PEI
    actividad_pei_info = serializers.SerializerMethodField()
    # Información de la tarea PEI
    tarea_pei_info = serializers.SerializerMethodField()
    # Información de las solicitudes relacionadas
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
            'fechaRendicion',
            'fechaActividad',
            'montoAsignado',
            'montoDescargado',
            'saldo',
            'descripcionActividad',
            'lugarActividad',
            'lugarRendicion',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'validacionContador',
            'validacionAdministrador',
            'estado_validacion',
            'estado_validacion_display',
            'responsable_info',
            'coordinador_info',
            'contador_info',
            'administrador_info',
            'fechaRendicion',
            'bloquearIconos',
            'actividad',
            'tarea',
            'actividad_pei_info',
            'tarea_pei_info',
            'detalleDestinoFondos',
            'solicitudFondos',
            'solicitudReembolso',
            'solicitudViaje',
            'solicitudPagoDirecto',
            'solicitud_fondos_info',
            'solicitud_reembolso_info',
            'solicitud_viaje_info',
            'solicitud_pago_directo_info'
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
        # Para rendiciones, todas las validaciones deben ser True para estar completamente validada
        if (obj.validacionResponsable and obj.validacionCoordinador and 
            obj.validacionContador and obj.validacionAdministrador):
            return 'completamente_validada'
        elif obj.validacionResponsable and not (obj.validacionCoordinador or obj.validacionContador or obj.validacionAdministrador):
            return 'validada_responsable'
        elif obj.validacionResponsable and obj.validacionCoordinador and not (obj.validacionContador or obj.validacionAdministrador):
            return 'validada_parcialmente'
        elif (obj.validacionResponsable and obj.validacionCoordinador and 
              obj.validacionContador and not obj.validacionAdministrador):
            return 'validada_contador'
        else:
            return 'pendiente'
    
    def get_estado_validacion_display(self, obj):
        estado = self.get_estado_validacion(obj)
        estados = {
            'completamente_validada': 'Validada Completamente',
            'validada_responsable': 'Validada por Responsable',
            'validada_parcialmente': 'Validada Parcialmente',
            'validada_contador': 'Validada por Contador',
            'pendiente': 'Pendiente'
        }
        return estados.get(estado, estado)
    
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
    
    def get_contador_info(self, obj):
        if obj.contador:
            return {
                'id': obj.contador.id,
                'nombre_completo': obj.contador.get_full_name(),
                'cargo': obj.contador.cargo
            }
        return None
    
    def get_administrador_info(self, obj):
        if obj.administrador:
            return {
                'id': obj.administrador.id,
                'nombre_completo': obj.administrador.get_full_name(),
                'cargo': obj.administrador.cargo
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
    
    def get_solicitud_fondos_info(self, obj):
        if obj.solicitudFondos:
            return {
                'id': obj.solicitudFondos.id,
                'numeroFormulario': obj.solicitudFondos.numeroFormulario,
                'montoSolicitado': float(obj.solicitudFondos.montoSolicitado) if obj.solicitudFondos.montoSolicitado else 0
            }
        return None
    
    def get_solicitud_reembolso_info(self, obj):
        if obj.solicitudReembolso:
            return {
                'id': obj.solicitudReembolso.id,
                'numeroFormulario': obj.solicitudReembolso.numeroFormulario,
                'montoSolicitado': float(obj.solicitudReembolso.montoSolicitado) if obj.solicitudReembolso.montoSolicitado else 0
            }
        return None
    
    def get_solicitud_viaje_info(self, obj):
        if obj.solicitudViaje:
            return {
                'id': obj.solicitudViaje.id,
                'numeroFormulario': obj.solicitudViaje.numeroFormulario,
                'montoSolicitado': float(obj.solicitudViaje.montoSolicitado) if obj.solicitudViaje.montoSolicitado else 0
            }
        return None
    
    def get_solicitud_pago_directo_info(self, obj):
        if obj.solicitudPagoDirecto:
            return {
                'id': obj.solicitudPagoDirecto.id,
                'numeroFormulario': obj.solicitudPagoDirecto.numeroFormulario,
                'montoSolicitado': float(obj.solicitudPagoDirecto.montoSolicitado) if obj.solicitudPagoDirecto.montoSolicitado else 0
            }
        return None
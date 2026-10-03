# serializers.py (en la misma carpeta) 
# spme/apptran/solreposicion/serializers/lista_sol_reposicion_por_actividad_serializer.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudReembolso, FormaPago
from spme_autenticacion.models import Usuario
from..services.estado_solicitud_service import EstadoSolicitudService

#Servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion

class SolicitudReembolsoSimpleSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar solicitudes de reembolso"""
    
    # Información del usuario que creó la solicitud
    solicitante = serializers.SerializerMethodField()
    # Información de validaciones
    estado_validacion = serializers.SerializerMethodField()
    # Nombre de la forma de pago
    forma_pago_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudReembolso
        fields = [
            'id',
            'numeroFormulario',
            'detalleDestinoFondos',
            'formaPago',
            'forma_pago_nombre',
            'lugarSolicitud',
            'fechaSolicitud',
            'montoSolicitado',
            'descripcion_actividad',
            'objetivo_actividad',
            'datos_forma_pago',
            'fechaRealizacionActividad',
            'bloquearIconos',
            'solicitante',
            'validacionResponsable',
            'validacionCoordinador',
            'estado_validacion',
            'actividad',
            'tarea'
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
        """
        Calcula el estado del documento
        """
        # 1. Recuperamos las validaciones ya pre-cargadas en RAM
        validaciones_memoria = list(obj.validaciones.all())
        
        # 2. Inicializamos el servicio
        service = ConsolidacionValidacionService()
        
        # 3. Evaluamos en memoria
        estado_consolidado = service.consolidar_desde_validaciones(
            tipo_solicitud="SOLICITUD_REEMBOLSO",
            validaciones=validaciones_memoria,
            metodo_resolucion=MetodoResolucion.DECISORIO
        )
        return estado_consolidado
        # estado = EstadoSolicitudService.get_estado_actual(obj)
        # return EstadoSolicitudService.get_estado_display(estado)
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else 'No especificada'
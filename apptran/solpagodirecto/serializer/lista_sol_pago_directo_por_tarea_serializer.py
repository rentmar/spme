# spme/apptran/solpagodirecto/serializer/lista_sol_pago_directo_por_tarea_serializer.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario
from ..services.estado_solicitud_service import EstadoSolicitudService

#Servicio de consolidacion
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService
from spme_validaciones.services.consolidacion.modelos import MetodoResolucion


class SolicitudPagoDirectoSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    forma_pago_nombre = serializers.SerializerMethodField()
    estado_validacion = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudPagoDirecto
        fields = [
            'id',
            'numeroFormulario',
            'detalleDestinoFondos',
            'formaPago',
            'forma_pago_nombre',
            'lugarSolicitud',
            'fechaSolicitud',
            'montoSolicitado',
            'fechaRealizacionActividad',
            'descripcion_actividad',
            'objetivo_actividad',
            'datos_forma_pago',
            'bloquearIconosSolFondos',
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
    
    def get_forma_pago_nombre(self, obj):
        return obj.formaPago.formaPago if obj.formaPago else None
    
    def get_estado_validacion(self, obj):
        """
        Calcula el estado de un documento
        """
        validaciones_memoria = list(obj.validaciones.all())
        
        # 2. Inicializamos el servicio
        service = ConsolidacionValidacionService()
        
        # 3. Evaluamos en memoria
        estado_consolidado = service.consolidar_desde_validaciones(
            tipo_solicitud="SOLICITUD_PAGO_DIRECTO",
            validaciones=validaciones_memoria,
            metodo_resolucion=MetodoResolucion.DECISORIO
        )
        
        return estado_consolidado
        # estado = EstadoSolicitudService.get_estado_actual(obj)
        # return EstadoSolicitudService.get_estado_display(estado)
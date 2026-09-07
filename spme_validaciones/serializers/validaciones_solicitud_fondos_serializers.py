#spme/spme_validaciones/serializers/validaciones_solicitud_fondos_serializers.py
from rest_framework import serializers
from ..models import ValidacionSolicitudFondos
from .validaciones_informes_actividad_subac_serializers import ValidacionBaseSerializer


class ValidacionSolicitudFondosSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de solicitud de fondos."""
    
    solicitud_codigo = serializers.CharField(
        source='solicitud.numeroFormulario', read_only=True
    )
    solicitud_monto = serializers.DecimalField(
        source='solicitud.montoSolicitado', read_only=True, max_digits=12, decimal_places=2
    )
    solicitud_tipo = serializers.SerializerMethodField()
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionSolicitudFondos
        fields = ValidacionBaseSerializer.Meta.fields + [
            'solicitud', 'solicitud_codigo', 'solicitud_monto', 'solicitud_tipo'
        ]
    
    def get_solicitud_tipo(self, obj):
        return obj.tipo_solicitud
    
    def get_tipo_documento(self, obj):
        return 'SOLICITUD_FONDOS'


class AsignarValidadoresSolicitudFondosSerializer(serializers.Serializer):
    """Serializer para asignar validadores a una solicitud de fondos."""
    
    validador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_validador_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No se permiten validador_ids duplicados")
        return value


class ResetearValidacionesSolicitudFondosSerializer(serializers.Serializer):
    """Serializer para resetear validaciones de solicitud de fondos."""
    
    nueva_version = serializers.CharField(default='2')


# ===================================================================
# SERIALIZERS PARA GESTIÓN DE REVISORES
# ===================================================================

class ListarRevisoresResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de listar revisores"""
    solicitud_id = serializers.IntegerField()
    solicitud_codigo = serializers.CharField()
    monto_solicitud = serializers.CharField()
    tipo_solicitud = serializers.CharField()
    total_revisores = serializers.IntegerField()
    resumen = serializers.DictField()
    revisores = serializers.ListField()


class ActualizarRevisoresSerializer(serializers.Serializer):
    """Serializer para actualizar revisores en lote"""
    cambios = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        required=True,
        help_text='Lista de cambios de revisor con validacion_id y nuevo_validador_id'
    )
    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text='Motivo del cambio (opcional)'
    )
    
    def validate_cambios(self, value):
        """
        Validar estructura de los cambios:
        - Cada cambio debe tener validacion_id y nuevo_validador_id
        - No debe haber duplicados
        """
        if not value:
            raise serializers.ValidationError('Debe proporcionar al menos un cambio')
        
        # Verificar que cada cambio tenga los campos requeridos
        for cambio in value:
            if 'validacion_id' not in cambio:
                raise serializers.ValidationError('Cada cambio debe tener validacion_id')
            if 'nuevo_validador_id' not in cambio:
                raise serializers.ValidationError('Cada cambio debe tener nuevo_validador_id')
        
        # Verificar validacion_id duplicados
        ids_validacion = [c['validacion_id'] for c in value]
        if len(ids_validacion) != len(set(ids_validacion)):
            raise serializers.ValidationError('No se permiten validacion_id duplicados')
        
        # Verificar nuevo_validador_id duplicados
        ids_validador = [c['nuevo_validador_id'] for c in value]
        if len(ids_validador) != len(set(ids_validador)):
            raise serializers.ValidationError('No se permiten nuevo_validador_id duplicados')
        
        return value


class ActualizarRevisoresResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de actualización de revisores"""
    mensaje = serializers.CharField()
    solicitud_id = serializers.IntegerField()
    solicitud_codigo = serializers.CharField()
    nueva_version = serializers.CharField()
    total_actualizados = serializers.IntegerField()
    resultados = serializers.ListField()
    notificaciones = serializers.DictField(required=False)
    errores = serializers.ListField(required=False)
# spme_validaciones/serializers.py
from rest_framework import serializers
from ..models import (
    Validacion, 
    ValidacionInformeActividad, 
    ValidacionInformeTarea,
    HistorialValidacion
)

# -------------------------------------------------------------------
# SERIALIZER BASE
# -------------------------------------------------------------------
class ValidacionBaseSerializer(serializers.ModelSerializer):
    """Serializer base con campos comunes"""
    validador_nombre = serializers.CharField(
        source='usuarioValidador.get_full_name', 
        read_only=True
    )
    redactor_nombre = serializers.CharField(
        source='usuarioRedactor.get_full_name',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    tipo_documento = serializers.SerializerMethodField()
    
    class Meta:
        model = Validacion
        fields = [
            'id', 'codigoSeguimiento',
            'usuarioValidador', 'validador_nombre',
            'usuarioRedactor', 'redactor_nombre',
            'estado', 'estado_display', 'comentarios',
            'versionDocumento',
            'fechaAsignacion', 'fechaResolucion',
            'tipo_documento'
        ]
        read_only_fields = ['codigoSeguimiento', 'fechaAsignacion', 'fechaResolucion']
    
    def get_tipo_documento(self, obj):
        if hasattr(obj, 'informe'):
            return 'ACTIVIDAD'
        elif hasattr(obj, 'informeTarea'):
            return 'TAREA'
        return 'DESCONOCIDO'


# -------------------------------------------------------------------
# SERIALIZER PARA ACTIVIDADES
# -------------------------------------------------------------------
class ValidacionInformeActividadSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de informe actividad"""
    informe_numero = serializers.CharField(
        source='informe.numeroInforme',
        read_only=True
    )
    informe_titulo = serializers.CharField(
        source='informe.objetivoActividad',
        read_only=True,
        allow_null=True
    )
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionInformeActividad
        fields = ValidacionBaseSerializer.Meta.fields + [
            'informe', 'informe_numero', 'informe_titulo'
        ]


# -------------------------------------------------------------------
# SERIALIZER PARA TAREAS
# -------------------------------------------------------------------
class ValidacionInformeTareaSerializer(ValidacionBaseSerializer):
    """Serializer para validaciones de informe tarea"""
    informe_numero = serializers.CharField(
        source='informeTarea.numeroInforme',
        read_only=True
    )
    informe_titulo = serializers.CharField(
        source='informeTarea.objetivoTarea',
        read_only=True,
        allow_null=True
    )
    
    class Meta(ValidacionBaseSerializer.Meta):
        model = ValidacionInformeTarea
        fields = ValidacionBaseSerializer.Meta.fields + [
            'informeTarea', 'informe_numero', 'informe_titulo'
        ]


# -------------------------------------------------------------------
# SERIALIZER PARA HISTORIAL
# -------------------------------------------------------------------
class HistorialValidacionSerializer(serializers.ModelSerializer):
    """Serializer para historial de validaciones"""
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name',
        read_only=True
    )
    validacion_codigo = serializers.CharField(
        source='validacion.codigoSeguimiento',
        read_only=True
    )
    validacion_tipo = serializers.SerializerMethodField()
    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display',
        read_only=True
    )
    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display',
        read_only=True
    )
    
    class Meta:
        model = HistorialValidacion
        fields = [
            'id', 'validacion', 'validacion_codigo', 'validacion_tipo',
            'usuario', 'usuario_nombre',
            'estado_anterior', 'estado_anterior_display',
            'estado_nuevo', 'estado_nuevo_display',
            'versionDocumento', 'comentario', 'fechaCambio'
        ]
        read_only_fields = ['fechaCambio']
    
    def get_validacion_tipo(self, obj):
        if hasattr(obj.validacion, 'informe'):
            return 'ACTIVIDAD'
        elif hasattr(obj.validacion, 'informeTarea'):
            return 'TAREA'
        return 'DESCONOCIDO'


# -------------------------------------------------------------------
# SERIALIZER PARA ASIGNAR VALIDADORES
# -------------------------------------------------------------------
class AsignarValidadoresSerializer(serializers.Serializer):
    """Serializer para asignar validadores a un informe"""
    TIPO_CHOICES = [
        ('actividad', 'Informe de Actividad'),
        ('tarea', 'Informe de Tarea'),
    ]
    
    tipo_documento = serializers.ChoiceField(choices=TIPO_CHOICES)
    documento_id = serializers.IntegerField()
    validador_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_validador_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No se permiten validador_ids duplicados")
        return value


# -------------------------------------------------------------------
# SERIALIZER PARA EMITIR VOTO
# -------------------------------------------------------------------
class EmitirVotoSerializer(serializers.Serializer):
    """Serializer para emitir un voto"""
    ESTADO_CHOICES = [
        ('APROBADO', 'Aprobar'),
        ('RECHAZADO', 'Rechazar'),
    ]
    
    estado = serializers.ChoiceField(choices=ESTADO_CHOICES)
    comentarios = serializers.CharField(
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        if data['estado'] == 'RECHAZADO' and not data.get('comentarios'):
            raise serializers.ValidationError(
                "Los comentarios son obligatorios cuando se rechaza"
            )
        return data


# -------------------------------------------------------------------
# SERIALIZER PARA CONSULTAR ESTADO
# -------------------------------------------------------------------
class EstadoValidacionSerializer(serializers.Serializer):
    """Serializer para respuesta de estado consolidado"""
    documento_id = serializers.IntegerField()
    documento_numero = serializers.CharField()
    tipo_documento = serializers.CharField()
    estado_consolidado = serializers.CharField()
    version_actual = serializers.CharField()
    resumen = serializers.DictField()
    validaciones = serializers.ListField()
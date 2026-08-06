from rest_framework import serializers

from spme_proyectos_reportes.models import (
    BitacoraPrincipalIndicadorOg,
    BitacoraPrincipalIndicadorOE,
    BitacoraPrincipalIndicadorRog,
    BitacoraPrincipalIndicadorRoe,
)


# ═══════════════════════════════════════════════════════
# SERIALIZER DE ENTRADA (Creación/Actualización)
# ═══════════════════════════════════════════════════════

class BitacoraCrearSerializer(serializers.Serializer):
    """Serializer para crear entradas de bitácora"""
    
    indicador_id = serializers.IntegerField(required=True)
    tipo_dato = serializers.ChoiceField(
        choices=['A-Z', '1-9', '%'],
        required=True
    )
    valor_literal = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    valor_numerico = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )
    valor_porcentual = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    fecha_registro = serializers.DateField(required=False)
    observaciones = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    archivos_adjuntos = serializers.JSONField(required=False)
    snapshot_indicador = serializers.JSONField(required=False)
    informe_actividad_id = serializers.IntegerField(required=False, allow_null=True)
    informe_tarea_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validar consistencia tipo_dato vs valor"""
        tipo_dato = data.get('tipo_dato')
        
        if tipo_dato == 'A-Z' and not data.get('valor_literal'):
            raise serializers.ValidationError({
                'valor_literal': 'Requerido para tipo de dato A-Z'
            })
        elif tipo_dato == '1-9' and data.get('valor_numerico') is None:
            raise serializers.ValidationError({
                'valor_numerico': 'Requerido para tipo de dato 1-9'
            })
        elif tipo_dato == '%' and data.get('valor_porcentual') is None:
            raise serializers.ValidationError({
                'valor_porcentual': 'Requerido para tipo de dato %'
            })
        
        return data


class BitacoraActualizarSerializer(serializers.Serializer):
    """Serializer para actualizar entradas (todos los campos opcionales)"""
    
    tipo_dato = serializers.ChoiceField(
        choices=['A-Z', '1-9', '%'], required=False
    )
    valor_literal = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    valor_numerico = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )
    valor_porcentual = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    fecha_registro = serializers.DateField(required=False)
    observaciones = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    archivos_adjuntos = serializers.JSONField(required=False)
    snapshot_indicador = serializers.JSONField(required=False)


# ═══════════════════════════════════════════════════════
# SERIALIZER DE CONSULTA (Filtros)
# ═══════════════════════════════════════════════════════

class BitacoraConsultaSerializer(serializers.Serializer):
    """Serializer para consultas con filtros de fecha"""
    
    fecha_inicio = serializers.DateField(required=True)
    fecha_fin = serializers.DateField(required=True)
    indicador_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """Validar que fecha_inicio <= fecha_fin"""
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError({
                'fecha_fin': 'Debe ser mayor o igual a fecha_inicio'
            })
        return data


# ═══════════════════════════════════════════════════════
# SERIALIZERS DE SALIDA (Respuesta) - Específicos por modelo
# ═══════════════════════════════════════════════════════

class BitacoraBaseSerializer(serializers.ModelSerializer):
    """Campos comunes a todas las bitácoras"""
    
    class Meta:
        fields = [
            'id',
            'tipo_indicador',
            'tipo_dato',
            'valor_literal',
            'valor_numerico',
            'valor_porcentual',
            'fecha_registro',
            'observaciones',
            'archivos_adjuntos',
            'usuario_registro',
            'timestamp_registro',
            'timestamp_ultima_modificacion',
            'snapshot_indicador',
        ]
        read_only_fields = [
            'id',
            'timestamp_registro',
            'timestamp_ultima_modificacion',
        ]


class BitacoraOGSerializer(BitacoraBaseSerializer):
    """Salida para bitácora OG"""
    
    class Meta(BitacoraBaseSerializer.Meta):
        model = BitacoraPrincipalIndicadorOg
        fields = BitacoraBaseSerializer.Meta.fields + [
            'indicador_og',
            'informe_actividad',
            'informe_tarea',
        ]


class BitacoraOESerializer(BitacoraBaseSerializer):
    """Salida para bitácora OE"""
    
    class Meta(BitacoraBaseSerializer.Meta):
        model = BitacoraPrincipalIndicadorOE
        fields = BitacoraBaseSerializer.Meta.fields + [
            'indicador_oe',
            'informe_actividad',
            'informe_tarea',
        ]


class BitacoraROGSerializer(BitacoraBaseSerializer):
    """Salida para bitácora ROG"""
    
    class Meta(BitacoraBaseSerializer.Meta):
        model = BitacoraPrincipalIndicadorRog
        fields = BitacoraBaseSerializer.Meta.fields + [
            'indicador_rog',
            'informe_actividad',
            'informe_tarea',
        ]


class BitacoraROESerializer(BitacoraBaseSerializer):
    """Salida para bitácora ROE"""
    
    class Meta(BitacoraBaseSerializer.Meta):
        model = BitacoraPrincipalIndicadorRoe
        fields = BitacoraBaseSerializer.Meta.fields + [
            'indicador_roe',
            'informe_actividad',
            'informe_tarea',
        ]
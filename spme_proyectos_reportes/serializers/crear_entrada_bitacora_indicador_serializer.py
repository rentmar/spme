# serializers.py
from rest_framework import serializers
from spme_proyectos_reportes.models import BitacoraIndicador
from spme_estructuracion_proyecto.models import (
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjEspecifico
)

class BitacoraIndicadorCreateSerializer(serializers.ModelSerializer):
    indicadorog = serializers.IntegerField(required=False, write_only=True)
    indicadoroe = serializers.IntegerField(required=False, write_only=True)
    indicadorrog = serializers.IntegerField(required=False, write_only=True)
    indicadorroe = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = BitacoraIndicador
        fields = [
            'fechaBitacora', 'cantidadAvance', 'reporteEscrito', 'linkSubida',
            'tipoIndicador', 'indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe'
        ]

    def validate(self, data):
        # Validar que solo se proporcione un tipo de indicador
        indicador_fields = ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']
        provided_fields = [field for field in indicador_fields if data.get(field) is not None]
        
        if len(provided_fields) != 1:
            raise serializers.ValidationError(
                "Debe proporcionar exactamente un tipo de indicador"
            )
        
        # Validar que tipoIndicador sea uno de los valores permitidos
        tipo_indicador = data.get('tipoIndicador')
        if tipo_indicador not in ['A-Z', '1-9', '%']:
            raise serializers.ValidationError({
                'tipoIndicador': 'Debe ser uno de: A-Z, 1-9, %'
            })
        
        # Validar cantidadAvance según el tipoIndicador
        cantidad_avance = data.get('cantidadAvance')
        if cantidad_avance:
            if tipo_indicador == '%':
                try:
                    porcentaje = float(cantidad_avance)
                    if porcentaje < 0 or porcentaje > 100:
                        raise serializers.ValidationError({
                            'cantidadAvance': 'El porcentaje debe estar entre 0 y 100'
                        })
                except ValueError:
                    raise serializers.ValidationError({
                        'cantidadAvance': 'Ingrese un valor numérico válido para porcentaje'
                    })
            
            elif tipo_indicador == '1-9':
                try:
                    valor = float(cantidad_avance)
                    if valor < 0:
                        raise serializers.ValidationError({
                            'cantidadAvance': 'El valor numérico no puede ser negativo'
                        })
                except ValueError:
                    raise serializers.ValidationError({
                        'cantidadAvance': 'Ingrese un valor numérico válido'
                    })
        
        return data

    def create(self, validated_data):
        # Extraer el indicador específico
        indicador = None
        tipo_indicador_detallado = None
        tipo_indicador_codigo = None
        id_hijo = None
        
        # Mapeo de campos a modelos y tipos
        tipo_map = {
            'indicadorog': {
                'model': IndicadorObjetivoGeneral,
                'tipo': 'Indicador de Objetivo General',
                'codigo': 'indicadorog'
            },
            'indicadoroe': {
                'model': IndicadorObjetivoEspecifico,
                'tipo': 'Indicador de Objetivo Específico',
                'codigo': 'indicadoroe'
            },
            'indicadorrog': {
                'model': IndicadorResultadoObjGral,
                'tipo': 'Indicador de Resultado de Objetivo General',
                'codigo': 'indicadorrog'
            },
            'indicadorroe': {
                'model': IndicadorResultadoObjEspecifico,
                'tipo': 'Indicador de Resultado de Objetivo Específico',
                'codigo': 'indicadorroe'
            }
        }
        
        for campo, info in tipo_map.items():
            if validated_data.get(campo):
                indicador_id = validated_data.pop(campo)
                try:
                    indicador = info['model'].objects.get(id=indicador_id)
                    tipo_indicador_detallado = info['tipo']
                    tipo_indicador_codigo = info['codigo']
                    id_hijo = indicador.id
                    break
                except info['model'].DoesNotExist:
                    raise serializers.ValidationError(
                        {campo: f"No existe un {info['tipo']} con ID {indicador_id}"}
                    )
        
        if not indicador:
            raise serializers.ValidationError("No se especificó un indicador válido")
        
        # Crear la bitácora usando el tipoIndicador del request
        bitacora = BitacoraIndicador.objects.create(
            indicador=indicador,
            **validated_data
        )
        
        # Guardar información adicional para la respuesta
        bitacora._respuesta_data = {
            'idindicador_base': indicador.indicadorproyecto_ptr_id,
            'idindicador_hijo': id_hijo,
            'tipo_indicador_detallado': tipo_indicador_detallado,
            'tipo_indicador_codigo': tipo_indicador_codigo,
            'idbitacora': bitacora.id,
            'codigo_indicador': indicador.codigo,
            'descripcion_indicador': indicador.descripcion,
            'tipo_dato_indicador': validated_data.get('tipoIndicador')  # El valor enviado en el request
        }
        
        return bitacora

class BitacoraIndicadorResponseSerializer(serializers.Serializer):
    mensaje_exito = serializers.BooleanField()
    traza_bitacora = serializers.DictField()
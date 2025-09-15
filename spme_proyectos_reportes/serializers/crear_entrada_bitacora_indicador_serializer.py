# serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    IndicadorProyecto, 
    IndicadorObjetivoGeneral, 
    IndicadorObjetivoEspecifico, 
    IndicadorResultadoObjGral, 
    IndicadorResultadoObjEspecifico)
from ..models import BitacoraIndicador

class BitacoraIndicadorCreateSerializer(serializers.ModelSerializer):
    idIndicador = serializers.IntegerField(write_only=True)
    tipoIndicador = serializers.CharField(write_only=True)
    
    class Meta:
        model = BitacoraIndicador
        fields = [
            'fechaBitacora', 
            'cantidadAvance', 
            'reporteEscrito', 
            'linkSubida', 
            'tipoIndicador',
            'idIndicador'
        ]
    
    def validate_tipoIndicador(self, value):
        tipos_validos = ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']
        if value not in tipos_validos:
            raise serializers.ValidationError(f"tipoIndicador debe ser uno de: {tipos_validos}")
        return value
    
    def create(self, validated_data):
        # Extraer datos específicos para el procesamiento
        id_indicador = validated_data.pop('idIndicador')
        tipo_indicador = validated_data.pop('tipoIndicador')
        
        # Mapear tipoIndicador a modelo concreto
        modelo_map = {
            'indicadorog': IndicadorObjetivoGeneral,
            'indicadoroe': IndicadorObjetivoEspecifico,
            'indicadorrog': IndicadorResultadoObjGral,
            'indicadorroe': IndicadorResultadoObjEspecifico
        }
        
        modelo_concreto = modelo_map.get(tipo_indicador)
        if not modelo_concreto:
            raise serializers.ValidationError("Tipo de indicador no válido")
        
        try:
            # Obtener la instancia del modelo concreto
            indicador_hijo = modelo_concreto.objects.get(id=id_indicador)
            # Obtener el id del padre (IndicadorProyecto)
            id_padre = indicador_hijo.indicadorproyecto_ptr_id
            
            # Crear la bitácora asociada al indicador padre
            bitacora = BitacoraIndicador.objects.create(
                indicador_id=id_padre,
                **validated_data
            )
            
            return bitacora
            
        except modelo_concreto.DoesNotExist:
            raise serializers.ValidationError(f"No se encontró el indicador con id {id_indicador} para el tipo {tipo_indicador}")
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear la bitácora: {str(e)}")
# serializers_simple.py
from rest_framework import serializers
from ..models import PlanificacionPei
from spme_estructuracion_pei.models import ActividadPei

class ActividadSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado que solo actualiza los campos básicos.
    Las relaciones many-to-many se manejan por separado.
    """
    
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre', 'presupuesto',
            'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
            'gradoEjecucion', 'procedencia_fondos', 'estado', 'estaInactiva',
            'tipo', 'pei', 'responsable'
        ]
    
    def to_internal_value(self, data):
        """Conversiones básicas"""
        data = data.copy() if isinstance(data, dict) else data
        
        # Manejar tipo
        if 'tipo' in data and isinstance(data['tipo'], str):
            tipo_str = data['tipo']
            if tipo_str and tipo_str != 'NODEF' and ' - ' in tipo_str:
                # Solo guardar el código
                data['tipo'] = tipo_str.split(' - ')[0]
        
        # Manejar responsable
        if 'responsable' in data and data['responsable'] == '':
            data['responsable'] = None
        
        return super().to_internal_value(data)

class ProcesarActividadesSimpleSerializer(serializers.Serializer):
    """
    Serializer simplificado para el endpoint.
    """
    actividades = serializers.ListField(child=serializers.DictField(), required=True)
    seguimiento = serializers.DictField(required=True)
    
    def validate(self, data):
        """Validación básica"""
        if not data.get('actividades'):
            raise serializers.ValidationError({
                'actividades': 'Debe proporcionar al menos una actividad'
            })
        
        if not data.get('seguimiento'):
            raise serializers.ValidationError({
                'seguimiento': 'Debe proporcionar datos de seguimiento'
            })
        
        return data
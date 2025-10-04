# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import InfTarea, TareaActividad
import json

class InfTareaSerializer(serializers.ModelSerializer):
    tarea_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = InfTarea
        fields = [
            'id',
            'numeroInforme',
            'fecha_ejecucion',
            'contribucion_proyecto',
            'avance_indicadores',
            'informacion_cuantitativa',
            'herramientas_evaluacion',
            'medios_verificacion',
            'comentarios_recomendaciones',
            'presupuesto_planificado',
            'presupuesto_ejecutado',
            'objetivo_actividad',
            'informe_objetivo_actividad',
            'tipo_actividad',
            'desglose_presupuesto',
            'tarea_id'
        ]
        read_only_fields = ['id', 'numeroInforme']

    def validate_contribucion_proyecto(self, value):
        """Validar que contribucion_proyecto sea JSON válido"""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Formato JSON inválido en contribucion_proyecto")
        return value

    def create(self, validated_data):
        tarea_id = validated_data.pop('tarea_id')
        
        try:
            tarea = TareaActividad.objects.get(id=tarea_id)
            validated_data['tarea'] = tarea
        except TareaActividad.DoesNotExist:
            raise serializers.ValidationError({"tarea_id": "La tarea especificada no existe"})
        
        # Generar número de informe automático
        if not validated_data.get('numeroInforme'):
            from django.utils import timezone
            count = InfTarea.objects.count() + 1
            validated_data['numeroInforme'] = f"INF-TAR-{timezone.now().strftime('%Y%m%d')}-{count:04d}"
        
        return super().create(validated_data)
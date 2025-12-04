from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei

#Serializador para la tarea de la actividad
class TareaActividadPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividadPei
        fields = '__all__'


class ActividadPeiSerializer(serializers.ModelSerializer):
    # Incluir las tareas relacionadas
    tareas_pei = TareaActividadPeiSerializer(many=True, read_only=True)
    
    # Campos para mostrar información de relaciones
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)
    pei_nombre = serializers.CharField(source='pei.nombre', read_only=True)
    
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado',
            'tipo', 'tipo_nombre', 'fecha_programada', 'fecha_inicio',
            'fecha_cierre', 'presupuesto', 'presupuestoGlobal',
            'totalReportado', 'totalEjecutado', 'saldo', 'gradoEjecucion',
            'procedencia_fondos', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion',
            'descripcion_tipo_actividad', 'responsable', 'responsable_nombre',
            'pei', 'pei_nombre', 'tareas_pei'
        ]
        depth = 1
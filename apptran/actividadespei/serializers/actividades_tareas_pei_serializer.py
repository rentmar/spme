from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei

class TareaActividadPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividadPei
        fields = '__all__'

class ActividadPeiSerializer(serializers.ModelSerializer):
    tareas_pei = TareaActividadPeiSerializer(many=True, read_only=True)
    
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'procedencia_fondos','totalReportado',
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'pei', 'tareas_pei', 'estaInactiva',
            'responsable',
        ]
         
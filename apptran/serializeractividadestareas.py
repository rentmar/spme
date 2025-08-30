from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad

class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'
        # fields = ['id', 'titulo', 'descripcion', 'estado', 'fecha_creacion', 
        #          'fecha_limite', 'presupuesto']

class ActividadSerializer(serializers.ModelSerializer):
    tareas = TareaActividadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'procedencia_fondos','totalReportado',
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'tareas'
        ]
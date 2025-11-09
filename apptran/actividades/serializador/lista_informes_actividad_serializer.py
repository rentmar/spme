#serializer.py
from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import InfActividad, InfTarea


class InfActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfActividad
        fields = '__all__'

class InfTareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfTarea
        fields = '__all__'

class TareaConTodosInformesSerializer(serializers.ModelSerializer):
    informes_tarea = serializers.SerializerMethodField()
    
    class Meta:
        model = TareaActividad
        fields = ['id', 'codigo', 'titulo', 'descripcion', 'estado', 'fecha_ejecucion', 
                 'fecha_creacion', 'fecha_limite', 'presupuesto', 'presupuestoDesglose', 
                 'informes_tarea']
    
    def get_informes_tarea(self, obj):
        # Obtener TODOS los informes de la tarea
        informes = InfTarea.objects.filter(tarea=obj).order_by('-fecha_ejecucion')
        return InfTareaSerializer(informes, many=True).data

class ActividadConTodosInformesSerializer(serializers.ModelSerializer):
    informes_actividad = serializers.SerializerMethodField()
    tareas_con_todos_informes = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = ['id', 'codigo', 'nombreCorto', 'descripcion', 'estado', 
                 'fecha_programada', 'fecha_inicio', 'fecha_cierre', 'presupuesto',
                 'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
                 'gradoEjecucion', 'procedencia_fondos', 'objetivo_de_actividad',
                 'descripcion_evaluacion', 'informes_actividad', 'tareas_con_todos_informes']
    
    def get_informes_actividad(self, obj):
        # Obtener TODOS los informes de la actividad
        informes = InfActividad.objects.filter(actividad=obj).order_by('-fecha_ejecucion')
        return InfActividadSerializer(informes, many=True).data
    
    def get_tareas_con_todos_informes(self, obj):
        # Obtener TODAS las tareas con TODOS sus informes
        tareas = TareaActividad.objects.filter(actividad=obj)
        return TareaConTodosInformesSerializer(tareas, many=True).data

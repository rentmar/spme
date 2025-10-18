# serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TipoActividad, TareaActividad
#from .models import TareaActividad, Actividad, TipoActividad, Proyecto

class ProyectoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'

class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = ['id', 'sigla', 'tipo_actividad']

class ActividadSimpleSerializer(serializers.ModelSerializer):
    tipo_info = TipoActividadSerializer(source='tipo', read_only=True)
    responsable_info = serializers.SerializerMethodField()
    proyecto_info = ProyectoSimpleSerializer(source='proyecto', read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'objetivo_de_actividad',
            'fecha_inicio', 'fecha_cierre', 'presupuesto', 'estado',
            'tipo_info', 'responsable_info', 'proyecto_info', 'procedencia_fondos',
            'estructuraProcedencia', 'rutaTrazadoIndicadores', 'factoresCriticos',
            'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo', 'gradoEjecucion'
        ]
    
    def get_responsable_info(self, obj):
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'nombre': obj.responsable.nombre,
                'paterno': obj.responsable.paterno,
                'materno': obj.responsable.materno,
                'cargo': obj.responsable.cargo,
            }
        return None

class TareaActividadDetailSerializer(serializers.ModelSerializer):
    actividad = ActividadSimpleSerializer(read_only=True)
    
    class Meta:
        model = TareaActividad
        fields = [
            'id', 'codigo', 'titulo', 'descripcion', 'estado',
            'fecha_creacion', 'fecha_ejecucion', 'fecha_limite',
            'presupuesto', 'presupuestoDesglose', 'actividad'
        ]
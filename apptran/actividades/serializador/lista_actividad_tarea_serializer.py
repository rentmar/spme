from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad, TipoActividad
from spme_autenticacion.models import Usuario


class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = [
            'id', 'estado', 'titulo', 'descripcion', 
            'fecha_creacion', 'fecha_limite', 'presupuesto'
        ]

class UsuarioResponsableSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'cargo']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()

class ActividadConTareasSerializer(serializers.ModelSerializer):
    tareas = TareaActividadSerializer(many=True, read_only=True)
    responsable_info = UsuarioResponsableSerializer(source='responsable', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado', 'estado_display',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre', 'presupuesto',
            'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
            'gradoEjecucion', 'responsable', 'responsable_info', 'tareas', 'estaInactiva'
        ]
        #depth = 1
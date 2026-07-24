from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    Proyecto, InstanciaGestora, ProcedenciaFondos
)
from spme_actividades.models import (
    Actividad,
    TareaActividad,
)

class TareaActividadSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo TareaActividad
    """
    class Meta:
        model = TareaActividad
        fields = [
            'id',
            'codigo',
            'titulo',
            'descripcion',
            'estado',
            'fecha_ejecucion',
            'fecha_creacion',
            'fecha_limite',
            'presupuesto',
            'presupuestoDesglose',
            'actividad',
        ]


class ActividadConTareasSerializer(serializers.ModelSerializer):
    """
    Serializador de Actividad incluyendo sus tareas relacionadas
    """
    tareas = TareaActividadSerializer(many=True, read_only=True)
    tipo_actividad = serializers.StringRelatedField(source='tipo')
    
    class Meta:
        model = Actividad
        fields = [
            'id',
            'codigo',
            'nombreCorto',
            'descripcion',
            'estado',
            'tipo_actividad',
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'presupuesto',
            'presupuestoGlobal',
            'totalEjecutado',
            'gradoEjecucion',
            'objetivo_de_actividad',
            'supuestos',
            'riesgos',
            'responsable',
            'tareas'
        ]


class InstanciaGestoraSerializer(serializers.ModelSerializer):
    """
    Serializador para InstanciaGestora
    """
    class Meta:
        model = InstanciaGestora
        fields = ['id', 'codigo', 'clasificador', 'instancia']


class ProcedenciaFondosSerializer(serializers.ModelSerializer):
    """
    Serializador para ProcedenciaFondos
    """
    class Meta:
        model = ProcedenciaFondos
        fields = ['id', 'sigla', 'financiera']


class ProyectoConActividadesSerializer(serializers.ModelSerializer):
    """
    Serializador principal: Proyecto -> Actividades -> Tareas
    """
    actividades = serializers.SerializerMethodField()
    instancias_gestoras = InstanciaGestoraSerializer(
        source='instancia_gestora', 
        many=True, 
        read_only=True
    )
    financiadores = ProcedenciaFondosSerializer(
        source='procedencia_fondos', 
        many=True, 
        read_only=True
    )
    propietario_nombre = serializers.StringRelatedField(source='propietario')
    
    class Meta:
        model = Proyecto
        fields = [
            'id',
            'codigo',
            'titulo',
            'descripcion',
            'estado',
            'fecha_inicio',
            'fecha_finalizacion',
            'fecha_creacion',
            'presupuesto',
            'esta_habilitado',
            'propietario_nombre',
            'instancias_gestoras',
            'financiadores',
            'pei',
            'programa',
            'actividades'
        ]
    
    def get_actividades(self, obj):
        """
        Obtiene las actividades activas del proyecto con sus tareas
        
        Args:
            obj (Proyecto): Instancia del proyecto
            
        Returns:
            list: Lista de actividades serializadas con sus tareas
        """
        actividades = obj.actividad_proyecto.filter(
            estaInactiva=False
        ).prefetch_related('tareas').order_by('fecha_programada', 'codigo')
        
        return ActividadConTareasSerializer(actividades, many=True).data
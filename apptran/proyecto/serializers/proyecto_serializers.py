#spme/apptran/proyecto/serializers/proyecto_serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    Proyecto, InstanciaGestora, ProcedenciaFondos
)
from spme_actividades.models import (
    Actividad,
    TareaActividad,
)
from spme_autenticacion.models import Usuario
from spme_estructuracion_pei.models import Pei
from spme_programas.models import Programa

class TareaActividadSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo TareaActividad
    """
    totalReportado = serializers.SerializerMethodField(read_only=True)
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
            'totalReportado', #Campo calculado
        ]
        read_only_fields = ['totalReportado']

    def get_totalReportado(self, obj):
        """
        Calcula dinámicamente el total reportado de la tarea
        """
        try:
            from spme_presupuesto.services.presupuesto_tree.calculos_presupuestos_ejecutados import (
                obtener_totales_tarea
            )
            totales = obtener_totales_tarea(obj.id)
            return float(totales.get('presupuesto_ejecutado', 0))
        except Exception:
            return 0.0



class ActividadConTareasSerializer(serializers.ModelSerializer):
    """
    Serializador de Actividad incluyendo sus tareas relacionadas
    """
    tareas = TareaActividadSerializer(many=True, read_only=True)
    tipo_actividad = serializers.StringRelatedField(source='tipo')
    tipo_actividad_id = serializers.IntegerField(source='tipo.id', read_only=True)
    responsable = serializers.StringRelatedField()  
    responsable_id = serializers.IntegerField(source='responsable.id', read_only=True) 
    totalReportado = serializers.SerializerMethodField(read_only=True)

    class Meta: 
        model = Actividad
        fields = [
            'id',
            'codigo',
            'nombreCorto',
            'descripcion',
            'estado',
            'tipo_actividad_id',
            'tipo_actividad',
            'responsable_id',       
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'presupuesto',
            'procedencia_fondos',
            'presupuestoGlobal',
            'totalEjecutado',
            'gradoEjecucion',
            'objetivo_de_actividad',
            'estructuraProcedencia',
            'supuestos',
            'riesgos',
            'responsable',
            'tareas',
            'totalReportado',
        ]
        read_only_fields = ['totalReportado'] 

    def get_totalReportado(self, obj):
        """
        Calcula dinámicamente el total reportado de la actividad
        Este campo se calcula en el servicio, no se almacena
        """
        try:
            from spme_presupuesto.services.presupuesto_tree.calculos_presupuestos_ejecutados import (
                obtener_totales_actividad
            )
            totales = obtener_totales_actividad(obj.id)
            return float(totales.get('presupuesto_ejecutado', 0))
        except Exception:
            return 0.0



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


# ─────────────────────────────────────────────────────────────
# Serializers para el endpoint /proyecto-resumen/{id}/
# ─────────────────────────────────────────────────────────────

class PeiResumenSerializer(serializers.ModelSerializer):
    """Serializador reducido de PEI."""
    class Meta:
        model = Pei
        fields = ['id', 'titulo']


class ProgramaResumenSerializer(serializers.ModelSerializer):
    """Serializador reducido de Programa."""
    class Meta:
        model = Programa
        fields = ['id', 'nombre']


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Serializador reducido de Usuario."""
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo']


class ProyectoResumenSerializer(serializers.ModelSerializer):
    """
    Serializador del proyecto para el endpoint /proyecto-resumen/{id}/.
    Devuelve solo los datos esenciales más las relaciones clave.
    """
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    pei = PeiResumenSerializer(read_only=True)
    programa = ProgramaResumenSerializer(read_only=True)
    propietario = UsuarioResumenSerializer(read_only=True)

    instancias_gestoras = InstanciaGestoraSerializer(
        source='instancia_gestora',
        many=True,
        read_only=True,
    )
    procedencias_fondos = ProcedenciaFondosSerializer(
        source='procedencia_fondos',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Proyecto
        fields = [
            'id',
            'codigo',
            'titulo',
            'descripcion',
            'estado',
            'estado_display',
            'esta_habilitado',
            'presupuesto',
            'fecha_inicio',
            'fecha_finalizacion',
            'pei',
            'programa',
            'propietario',
            'instancias_gestoras',
            'procedencias_fondos',
        ]
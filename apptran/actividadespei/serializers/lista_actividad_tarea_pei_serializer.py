# serializers.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_estructuracion_pei.models import ActividadPei, TareaActividadPei
from spme_actividades.models import TipoActividad

class ActividadPeiSerializer(serializers.ModelSerializer):
    # Responsable
    responsable = serializers.IntegerField(source='responsable_id', read_only=True)
    responsable_info = serializers.SerializerMethodField()
    
    # Tipo como objeto (no tipo_info)
    tipo = serializers.SerializerMethodField()
    
    # PEI 
    pei = serializers.IntegerField(source='pei_id', read_only=True)
    
    # Tareas
    tarea = serializers.SerializerMethodField()
    
    # Campos ManyToMany como arrays de IDs
    objetivos_pei = serializers.SerializerMethodField()
    factores_criticos = serializers.SerializerMethodField()
    indicadores_cuantitativos = serializers.SerializerMethodField()
    indicadores_cualitativos = serializers.SerializerMethodField()
    
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos',
            'riesgos', 'objetivo_de_actividad', 'descripcion_evaluacion',
            'descripcion_tipo_actividad', 
            'responsable',  # ID del responsable
            'responsable_info',  # Objeto completo del responsable
            'tipo',  # Objeto tipo (no tipo_info)
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado',
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'pei',  # ID del PEI
            'objetivos_pei', 'factores_criticos',
            'indicadores_cuantitativos', 'indicadores_cualitativos', 'tarea'
        ]
    
    def get_responsable_info(self, obj):
        """Retorna objeto completo del responsable"""
        if obj.responsable:
            return {
                'id': obj.responsable.id,
                'username': obj.responsable.username,
                'nombre_completo': f"{obj.responsable.nombre} {obj.responsable.paterno} {obj.responsable.materno}".strip(),
                'cargo': obj.responsable.cargo
            }
        return None
    
    def get_tipo(self, obj):
        """Retorna objeto tipo (no tipo_info)"""
        if obj.tipo:
            return {
                'id': obj.tipo.id,
                'sigla': obj.tipo.sigla,
                'tipo_actividad': obj.tipo.tipo_actividad
            }
        return None
    
    def get_tarea(self, obj):
        """Retorna array de tareas"""
        tareas = obj.tareas_pei.all()
        return [
            {
                'id': t.id,
                'estado': t.estado,
                'codigo': t.codigo,
                'titulo': t.titulo,
                'descripcion': t.descripcion,
                'fecha_ejecucion': t.fecha_ejecucion,
                'fecha_creacion': t.fecha_creacion,
                'fecha_limite': t.fecha_limite,
                'presupuestoDesglose': t.presupuestoDesglose,
                'presupuesto': t.presupuesto,
                'actividad': t.actividad_id  # ID de la actividad
            }
            for t in tareas
        ]
    
    def get_objetivos_pei(self, obj):
        return list(obj.objetivos_pei.values_list('id', flat=True))
    
    def get_factores_criticos(self, obj):
        return list(obj.factores_criticos.values_list('id', flat=True))
    
    def get_indicadores_cuantitativos(self, obj):
        return list(obj.indicadores_cuantitativos.values_list('id', flat=True))
    
    def get_indicadores_cualitativos(self, obj):
        return list(obj.indicadores_cualitativos.values_list('id', flat=True))
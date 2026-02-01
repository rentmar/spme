from rest_framework import serializers

from spme_actividades.models import (
    Actividad, 
    TareaActividad,
    TipoActividad,
    )

from spme_monitoreo.models import (
    InformeActividadPrincipal,
    InformeTareaPrincipal,
)

class TipoActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActividad
        fields = ['id', 'sigla', 'tipo_actividad']

class InformeTareaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeTareaPrincipal
        fields = [
            'id', 'numeroInforme', 'fechaEjecucion', 'objetivoTarea',
            'informeObjetivoTarea', 'tipoActividad', 'desglosePresupuesto',
            'contribucionProyecto', 'avanceIndicadores',
            'informacionCuantitativa', 'herramientasEvaluacion',
            'mediosVerificacion', 'comentariosRecomendaciones',
            'presupuestoPlanificado', 'presupuestoEjecutado'
        ]

class InformeActividadPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeActividadPrincipal
        fields = [
            'id', 'numeroInforme', 'fechaEjecucion', 'objetivoActividad',
            'informeObjetivoActividad', 'tipoActividad', 'reporteTipo',
            'procedenciaFondos', 'observacionesPresupuesto',
            'archivosCuantitativos', 'herramientasArchivos',
            'mediosArchivos', 'contribucionProyecto', 'avanceIndicadores',
            'informacionCuantitativa', 'herramientasEvaluacion',
            'mediosVerificacion', 'comentariosRecomendaciones',
            'presupuestoPlanificado', 'presupuestoEjecutado'
        ]

class TareaActividadSerializer(serializers.ModelSerializer):
    informes_tarea = InformeTareaPrincipalSerializer(
        source='tarea_informes_de_subactividad_principal', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = TareaActividad
        fields = [
            'id', 'codigo', 'titulo', 'descripcion', 'estado',
            'fecha_ejecucion', 'fecha_creacion', 'fecha_limite',
            'presupuesto', 'presupuestoDesglose', 'informes_tarea'
        ]

class ActividadSerializer(serializers.ModelSerializer):
    tipo_info = TipoActividadSerializer(source='tipo', read_only=True)
    tareas = TareaActividadSerializer(many=True, read_only=True)
    informes_actividad = InformeActividadPrincipalSerializer(
        source='actividad_informes_de_actividad_principal', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado',
            'tipo', 'tipo_info', 'fecha_programada', 'fecha_inicio',
            'fecha_cierre', 'presupuesto', 'presupuestoGlobal',
            'totalReportado', 'totalEjecutado', 'saldo', 'gradoEjecucion',
            'procedencia_fondos', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion',
            'descripcion_tipo_actividad', 'rutaTrazadoIndicadores',
            'factoresCriticos', 'estructuraProcedencia', 'estaInactiva',
            'tareas', 'informes_actividad'
        ]

class ActividadInformesCompletosSerializer(serializers.ModelSerializer):
    """Serializer para todos los informes de una actividad y sus tareas"""
    tipo_info = TipoActividadSerializer(source='tipo', read_only=True)
    
    # Informes de la actividad principal
    informes_actividad = InformeActividadPrincipalSerializer(
        source='actividad_informes_de_actividad_principal', 
        many=True, 
        read_only=True
    )
    
    # Tareas con sus informes
    tareas_con_informes = serializers.SerializerMethodField()
    
    # Estadísticas de informes
    estadisticas_informes = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'estado',
            'tipo_info', 'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'totalEjecutado', 'gradoEjecucion',
            'informes_actividad', 'tareas_con_informes', 'estadisticas_informes'
        ]
    
    def get_tareas_con_informes(self, obj):
        """Obtiene todas las tareas con sus informes relacionados"""
        tareas = obj.tareas.all()
        tareas_data = []
        
        for tarea in tareas:
            informes = tarea.tarea_informes_de_subactividad_principal.all()
            tarea_data = {
                'id': tarea.id,
                'codigo': tarea.codigo,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'estado': tarea.estado,
                'fecha_ejecucion': tarea.fecha_ejecucion,
                'fecha_limite': tarea.fecha_limite,
                'presupuesto': tarea.presupuesto,
                'total_informes': informes.count(),
                'informes': InformeTareaPrincipalSerializer(informes, many=True).data
            }
            tareas_data.append(tarea_data)
        
        return tareas_data
    
    def get_estadisticas_informes(self, obj):
        """Calcula estadísticas de informes"""
        total_informes_actividad = obj.actividad_informes_de_actividad_principal.count()
        
        total_informes_tareas = 0
        for tarea in obj.tareas.all():
            total_informes_tareas += tarea.tarea_informes_de_subactividad_principal.count()
        
        total_general = total_informes_actividad + total_informes_tareas
        
        return {
            'total_informes_actividad': total_informes_actividad,
            'total_informes_tareas': total_informes_tareas,
            'total_general': total_general,
            'cantidad_tareas': obj.tareas.count()
        }
    

#Serializadores para los resumenes


class TipoActividadResumenSerializer(serializers.ModelSerializer):
    """Serializer simplificado para tipo de actividad en resumen"""
    class Meta:
        model = TipoActividad
        fields = ['id', 'sigla', 'tipo_actividad']

class ActividadResumenSerializer(serializers.ModelSerializer):
    """
    Serializer específico para mostrar resumen de actividades
    con conteos de informes y tareas
    """
    tipo_info = TipoActividadResumenSerializer(source='tipo', read_only=True)
    
    # Campos anotados desde la vista
    total_informes_actividad = serializers.IntegerField(read_only=True)
    total_tareas = serializers.IntegerField(read_only=True)
    total_informes_tareas = serializers.IntegerField(read_only=True)
    total_informes_general = serializers.SerializerMethodField()
    
    # Responsable información básica
    responsable_nombre = serializers.SerializerMethodField()
    
    # Proyecto información básica
    proyecto_nombre = serializers.SerializerMethodField()
    
    # Fechas formateadas
    fecha_inicio_formatted = serializers.SerializerMethodField()
    fecha_cierre_formatted = serializers.SerializerMethodField()
    
    # Estado con display
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'estado', 'estado_display',
            'tipo_info', 'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'fecha_inicio_formatted', 'fecha_cierre_formatted',
            'presupuesto', 'totalEjecutado', 'gradoEjecucion', 'descripcion',
            'total_informes_actividad', 'total_tareas', 'total_informes_tareas',
            'total_informes_general', 'responsable_nombre', 'proyecto_nombre'
        ]
        read_only_fields = fields
    
    def get_total_informes_general(self, obj):
        """Calcula el total general de informes (actividad + tareas)"""
        return getattr(obj, 'total_informes_actividad', 0) + getattr(obj, 'total_informes_tareas', 0)
    
    def get_responsable_nombre(self, obj):
        """Obtiene nombre del responsable"""
        if obj.responsable:
            return f"{obj.responsable.first_name} {obj.responsable.last_name}"
        return "Sin asignar"
    
    def get_proyecto_nombre(self, obj):
        """Obtiene nombre del proyecto"""
        if obj.proyecto:
            return obj.proyecto.nombre
        return "Sin proyecto"
    
    def get_fecha_inicio_formatted(self, obj):
        """Formatea fecha de inicio"""
        if obj.fecha_inicio:
            return obj.fecha_inicio.strftime('%d/%m/%Y')
        return None
    
    def get_fecha_cierre_formatted(self, obj):
        """Formatea fecha de cierre"""
        if obj.fecha_cierre:
            return obj.fecha_cierre.strftime('%d/%m/%Y')
        return None    
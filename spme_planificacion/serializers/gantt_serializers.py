# spme_planificacion/serializers/gantt_serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import Proyecto
from spme_actividades.models import Actividad, TareaActividad


class ProyectoGanttSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    open = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = ['id', 'text', 'start_date', 'duration', 'progress', 'estado', 'parent', 'open', 'type']

    def get_text(self, obj):
        return f"🏗️ {obj.titulo}"

    def get_start_date(self, obj):
        return obj.fecha_inicio if obj.fecha_inicio else obj.fecha_creacion.date()

    def get_duration(self, obj):
        if obj.fecha_inicio and obj.fecha_finalizacion:
            return (obj.fecha_finalizacion - obj.fecha_inicio).days
        return 365

    def get_progress(self, obj):
        return 0

    def get_parent(self, obj):
        return 0

    def get_open(self, obj):
        return False

    def get_type(self, obj):
        return 'project'


class ActividadGanttSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    open = serializers.SerializerMethodField()

    class Meta:
        model = Actividad
        fields = ['id', 'text', 'start_date', 'duration', 'progress', 'estado', 'parent', 'open']

    def get_id(self, obj):
        return obj.id + 100000

    def get_text(self, obj):
        return f"📋 {obj.nombreCorto}"

    def get_start_date(self, obj):
        return obj.fecha_inicio

    def get_duration(self, obj):
        if obj.fecha_inicio and obj.fecha_cierre:
            return (obj.fecha_cierre - obj.fecha_inicio).days
        return 30

    def get_progress(self, obj):
        return 0

    def get_parent(self, obj):
        return obj.proyecto_id if obj.proyecto_id else 0

    def get_open(self, obj):
        return False


class TareaGanttSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    start_date = serializers.CharField(source='fecha_creacion')
    duration = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    open = serializers.SerializerMethodField()

    class Meta:
        model = TareaActividad
        fields = ['id', 'text', 'start_date', 'duration', 'progress', 'estado', 'parent', 'open']

    def get_id(self, obj):
        return obj.id + 200000

    def get_text(self, obj):
        return f"🏷️ {obj.titulo}"

    def get_duration(self, obj):
        if obj.fecha_creacion and obj.fecha_limite:
            return (obj.fecha_limite - obj.fecha_creacion).days
        return 7

    def get_progress(self, obj):
        return 0

    def get_parent(self, obj):
        return obj.actividad_id + 100000 if obj.actividad_id else 0

    def get_open(self, obj):
        return False
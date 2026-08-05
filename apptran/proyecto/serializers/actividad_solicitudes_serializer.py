# api/v2/serializers/actividad_solicitudes_serializer.py

from rest_framework import serializers


class BadgeSerializer(serializers.Serializer):
    creadas = serializers.IntegerField(default=0)
    aprobadas = serializers.IntegerField(default=0)
    rechazadas = serializers.IntegerField(default=0)
    pendientes = serializers.IntegerField(default=0)
    borradores = serializers.IntegerField(default=0)


class BadgesSerializer(serializers.Serializer):
    fondos = BadgeSerializer()
    viajes = BadgeSerializer()
    pagos_directos = BadgeSerializer()
    reposiciones = BadgeSerializer()


class ResponsableSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()


class ProyectoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()


class TareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField(allow_blank=True)
    descripcion = serializers.CharField(allow_blank=True)
    estado = serializers.CharField()
    codigo = serializers.CharField(allow_blank=True)
    badges = BadgesSerializer()


class ActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_blank=True)
    nombre_corto = serializers.CharField(allow_blank=True)
    descripcion = serializers.CharField(allow_blank=True)
    estado = serializers.CharField()
    presupuesto = serializers.FloatField(default=0)
    procedencia_fondos = serializers.JSONField(default=dict, allow_null=True)
    fecha_programada = serializers.DateField(allow_null=True)
    duracion = serializers.IntegerField(allow_null=True)
    fecha_inicio = serializers.DateField(allow_null=True)
    fecha_cierre = serializers.DateField(allow_null=True)
    responsable = ResponsableSerializer(allow_null=True)
    proyecto = ProyectoSerializer(allow_null=True)
    badges = BadgesSerializer()
    tareas = TareaSerializer(many=True)


class PaginacionSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()


class ActividadSolicitudesResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    results = ActividadSerializer(many=True)
    pagination = PaginacionSerializer()
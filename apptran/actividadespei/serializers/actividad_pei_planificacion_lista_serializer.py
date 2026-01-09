# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import ActividadPei


class ActividadPeiListaPlanificacion(serializers.ModelSerializer):
    """
    Serializer específico para el endpoint actividades/pei/idpei/
    Devuelve el formato exacto solicitado para la planificacion
    """
    # Campo tipo como valor choice (sigla)
    tipo = serializers.SerializerMethodField()
    # Campo responsable como username (no ID)
    responsable = serializers.SerializerMethodField()
    pei = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ActividadPei
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'estaInactiva', 'tipo', 'pei', 'responsable',
        ]

    def get_tipo(self, obj):
        """
        Devuelve la sigla del tipo de actividad.
        """
        if obj.tipo:
            return obj.tipo.sigla if obj.tipo.sigla else "OTRO"
        return "NODEF"
    
    def get_responsable(self, obj):
        """
        Devuelve el username del responsable o null.
        """
        if obj.responsable:
            return obj.responsable.username
        return None    
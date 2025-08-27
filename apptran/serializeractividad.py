# serializers.py
from rest_framework import serializers
from spme_actividades.models import Actividad

class ActividadProyectoSerializer(serializers.ModelSerializer):
    """
    Serializer específico para el endpoint actividades/proyecto/idproyecto/
    Devuelve el formato exacto solicitado
    """
    
    # Campo tipo como valor choice (sigla)
    tipo = serializers.SerializerMethodField()
    
    # Campo responsable como username (no ID)
    responsable = serializers.SerializerMethodField()
    
    # Campos de relaciones (solo el ID, no objetos anidados)
    proceso = serializers.PrimaryKeyRelatedField(read_only=True)
    resultado_og = serializers.PrimaryKeyRelatedField(read_only=True)
    resultado_oe = serializers.PrimaryKeyRelatedField(read_only=True)
    producto_oe = serializers.PrimaryKeyRelatedField(read_only=True)
    objetivo_pei = serializers.PrimaryKeyRelatedField(read_only=True)
    indicador_pei = serializers.PrimaryKeyRelatedField(read_only=True)
    proyecto = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'tipo', 'proceso', 'resultado_og', 'resultado_oe', 
            'producto_oe', 'objetivo_pei', 'indicador_pei', 'proyecto', 'responsable', 'rutaTrazadoIndicadores', 'factoresCriticos',
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
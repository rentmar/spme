# serializers.py
from rest_framework import serializers
from spme_actividades.models import Actividad



class ActividadGanntSerializer(serializers.ModelSerializer):
    nombre_responsable = serializers.SerializerMethodField()
    nombre_corto = serializers.CharField(source='nombreCorto')
    grado_ejecucion = serializers.CharField(source='gradoEjecucion', read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'nombre_responsable', 'codigo', 'nombre_corto', 'descripcion',
            'tipo', 'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'grado_ejecucion', 'estado'
        ]
    
    def get_nombre_responsable(self, obj):
        if obj.responsable:
            # Usar el método get_full_name() del modelo Usuario
            nombre_completo = obj.responsable.get_full_name()
            return nombre_completo if nombre_completo else "Sin Responsable"
        return "Sin Responsable"
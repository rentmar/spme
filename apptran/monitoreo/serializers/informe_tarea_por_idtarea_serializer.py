# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import InfTarea

class InfTareaSerializer(serializers.ModelSerializer):
    tarea_codigo = serializers.CharField(source='tarea.codigo', read_only=True)
    tarea_titulo = serializers.CharField(source='tarea.titulo', read_only=True)
    
    class Meta:
        model = InfTarea
        fields = [
            'id',
            'numeroInforme',
            'fecha_ejecucion',
            'contribucion_proyecto',
            'avance_indicadores',
            'informacion_cuantitativa',
            'herramientas_evaluacion',
            'medios_verificacion',
            'comentarios_recomendaciones',
            'presupuesto_planificado',
            'presupuesto_ejecutado',
            'objetivo_tarea',
            'informe_objetivo_tarea',
            'tipo_actividad',
            'desglose_presupuesto',
            'tarea',
            'tarea_codigo',
            'tarea_titulo'
        ]
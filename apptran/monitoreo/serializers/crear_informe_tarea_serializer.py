# serializers.py
from rest_framework import serializers
from django.db import transaction
from spme_estructuracion_proyecto.models import (
    IndicadorObjetivoGeneral,
    IndicadorObjetivoEspecifico,
    IndicadorResultadoObjGral,
    IndicadorResultadoObjEspecifico
)
from spme_monitoreo.models import InfTarea
from spme_proyectos_reportes.models import (
    BitacoraIndicadorOG,
    BitacoraIndicadorOE,
    BitacoraIndicadorROG,
    BitacoraIndicadorROE,
    )
from spme_actividades.models import TareaActividad

class BitacoraAvanceSerializer(serializers.Serializer):
    """Serializer para validar los datos de avance de indicadores"""
    id = serializers.CharField()
    type = serializers.ChoiceField(choices=[
        'indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe'
    ])
    tipo_dato = serializers.ChoiceField(choices=['A-Z', '1-9', '%'])
    nodoproyecto = serializers.DictField()
    datosRegistrados = serializers.DictField()

    def validate_nodoproyecto(self, value):
        """Valida que el nodoproyecto tenga la estructura correcta"""
        if 'id' not in value:
            raise serializers.ValidationError("El campo 'id' es requerido en nodoproyecto")
        return value

    def validate_datosRegistrados(self, value):
        """Valida los datos registrados"""
        required_fields = ['valor', 'fecha_registro']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"El campo '{field}' es requerido en datosRegistrados")
        return value

class InfTareaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear InfTarea con bitácoras"""
    
    # ✅ CORRECCIÓN: Usamos JSONField para avance_indicadores
    avance_en_indicador = serializers.JSONField(
        required=False,
        write_only=True,
        source='avance_indicadores'  # 👈 Se guarda como JSON en avance_indicadores
    )
    
    # Campos que vienen del formulario con nombres diferentes
    descripcion_herramientas = serializers.CharField(
        required=False, 
        allow_blank=True, 
        write_only=True,
        source='herramientas_evaluacion'
    )
    objetivo_subactividad = serializers.CharField(
        required=False, 
        allow_blank=True, 
        write_only=True,
        source='objetivo_tarea'
    )
    informe_objetivo_subactividad = serializers.CharField(
        required=False, 
        allow_blank=True, 
        write_only=True,
        source='informe_objetivo_tarea'
    )

    class Meta:
        model = InfTarea
        fields = [
            # Campos del formulario que se mapean automáticamente
            'tarea', 'fecha_ejecucion', 'contribucion_proyecto',
            'informacion_cuantitativa', 'medios_verificacion',
            'comentarios_recomendaciones', 'presupuesto_planificado',
            'presupuesto_ejecutado', 'tipo_actividad', 'desglose_presupuesto',
            
            # ✅ CORRECCIÓN: avance_en_indicador se guarda como JSON en avance_indicadores
            'avance_en_indicador',
            
            # Campos mapeados del formulario
            'descripcion_herramientas', 'objetivo_subactividad', 'informe_objetivo_subactividad'
        ]
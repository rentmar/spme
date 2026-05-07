from rest_framework import serializers
from spme_estructuracion_proyecto.models import (
    Proyecto,
    InstanciaGestora,
    ProcedenciaFondos,
)
from spme_estructuracion_pei.models import Pei
from spme_programas.models import Programa
from spme_autenticacion.models import Usuario

class InstanciaGestoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstanciaGestora
        fields = '__all__'

class ProcedenciaFondosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedenciaFondos
        fields = '__all__'

class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = '__all__'

class PeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pei
        fields = '__all__'

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

# Serializador para información resumida
class ProyectoResumenSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    propietario_nombre = serializers.SerializerMethodField()
    programa_nombre = serializers.SerializerMethodField()
    pei_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Proyecto
        fields = [
            'id',
            'codigo',
            'titulo',
            'estado',
            'estado_display',
            'presupuesto',
            'fecha_inicio',
            'fecha_finalizacion',
            'propietario_nombre',
            'programa_nombre',
            'pei_nombre',
        ]
    
    def get_propietario_nombre(self, obj):
        if obj.propietario:
            return f"{obj.propietario.nombre} {obj.propietario.paterno}".strip() or obj.propietario.username
        return None
    
    def get_programa_nombre(self, obj):
        return obj.programa.nombre if obj.programa else None
    
    def get_pei_nombre(self, obj):
        return obj.pei.nombre if hasattr(obj.pei, 'nombre') else str(obj.pei) if obj.pei else None

# Proyectos Habilitados - Información completa
class ProyectoHabilitadoSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    propietario = PropietarioSerializer(read_only=True)
    pei = PeiSerializer(read_only=True)
    programa = ProgramaSerializer(read_only=True) 
    instancia_gestora = InstanciaGestoraSerializer(many=True, read_only=True)
    procedencia_fondos = ProcedenciaFondosSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            'id', 
            'codigo', 
            'titulo', 
            'descripcion',
            'fecha_creacion', 
            'fecha_inicio', 
            'fecha_finalizacion',
            'presupuesto', 
            'estado', 
            'estado_display', 
            'esta_habilitado',
            'creado_por',  
            'propietario', 
            'pei', 
            'programa',
            'instancia_gestora', 
            'procedencia_fondos'
        ]
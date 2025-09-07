# serializers.py
from rest_framework import serializers
from spme_estructuracion_proyecto.models import Proyecto, ProcedenciaFondos, InstanciaGestora
from spme_estructuracion_pei.models import Pei

class PeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pei
        fields = '__all__'

class ProcedenciaFondosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedenciaFondos
        fields = '__all__'

class InstanciaGestoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstanciaGestora
        fields = '__all__'

class ProyectoDetailSerializer(serializers.ModelSerializer):
    # Información del PEI asociado
    pei = PeiSerializer(read_only=True)
    
    # Lista de instancias gestoras
    instancia_gestora = InstanciaGestoraSerializer(many=True, read_only=True)
    
    # Lista de procedencias de fondos
    procedencia_fondos = ProcedenciaFondosSerializer(many=True, read_only=True)
    
    # Estado legible
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
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
            'creado_por',
            'pei',
            'instancia_gestora',
            'procedencia_fondos'
        ]
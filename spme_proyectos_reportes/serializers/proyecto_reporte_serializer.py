from rest_framework import serializers
from spme_estructuracion_proyecto.models import *

class ProductoROESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoResultadoOE
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos', 'entregado']

class IndicadorResultadoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjEspecifico
        fields = ['id', 'codigo', 'descripcion', 'redaccion', 'fuente_verificacion']

class ResultadoOESerializer(serializers.ModelSerializer):
    productos_res_oe = ProductoROESerializer(many=True, read_only=True)
    indicador_res_oe = IndicadorResultadoOESerializer(many=True, read_only=True)  # Corregido: singular
    
    class Meta:
        model = ResultadoOE
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos', 
                 'productos_res_oe', 'indicador_res_oe']  # Corregido: singular

class ProductoOESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoOE
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos', 'entregado']

class IndicadorOESerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoEspecifico
        fields = ['id', 'codigo', 'descripcion', 'redaccion', 'fuente_verificacion']

class ObjetivoEspecificoSerializer(serializers.ModelSerializer):
    productos_oe = ProductoOESerializer(many=True, read_only=True)
    resultados_oe = ResultadoOESerializer(many=True, read_only=True)
    indicador_oe = IndicadorOESerializer(many=True, read_only=True)  # Corregido: singular
    
    class Meta:
        model = ObjetivoEspecificoProyecto
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos',
                 'productos_oe', 'resultados_oe', 'indicador_oe']  # Corregido: singular

class IndicadorResultadoOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorResultadoObjGral
        fields = ['id', 'codigo', 'descripcion', 'redaccion', 'fuente_verificacion']

class ResultadoOGSerializer(serializers.ModelSerializer):
    indicador_res_og = IndicadorResultadoOGSerializer(many=True, read_only=True)  # Corregido: singular
    
    class Meta:
        model = ResultadoOG
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos', 'indicador_res_og']  # Corregido: singular

class IndicadorOGSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorObjetivoGeneral
        fields = ['id', 'codigo', 'descripcion', 'redaccion', 'fuente_verificacion']

class ObjetivoGeneralSerializer(serializers.ModelSerializer):
    resultados_og = ResultadoOGSerializer(many=True, read_only=True)
    indicador_og = IndicadorOGSerializer(many=True, read_only=True)  # Corregido: singular
    objetivos_especificos_og = ObjetivoEspecificoSerializer(many=True, read_only=True)  # Corregido: relación correcta
    
    class Meta:
        model = ObjetivoGeneralProyecto
        fields = ['id', 'codigo', 'descripcion', 'supuestos', 'riesgos',
                 'resultados_og', 'indicador_og', 'objetivos_especificos_og']  # Corregidos

class InstanciaGestoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstanciaGestora
        fields = ['id', 'codigo', 'clasificador', 'instancia']

class ProcedenciaFondosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedenciaFondos
        fields = ['id', 'sigla', 'financiera']

class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = ['id', 'codigo', 'nombre']

class ProyectoReporteSerializer(serializers.ModelSerializer):
    objetivo_general = ObjetivoGeneralSerializer(read_only=True)
    instancia_gestora = InstanciaGestoraSerializer(many=True, read_only=True)
    procedencia_fondos = ProcedenciaFondosSerializer(many=True, read_only=True)
    programa = ProgramaSerializer(read_only=True)
    
    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'titulo', 'descripcion', 'fecha_creacion',
            'fecha_inicio', 'fecha_finalizacion', 'presupuesto', 'estado',
            'creado_por', 'objetivo_general', 'instancia_gestora',
            'procedencia_fondos', 'programa'
        ]
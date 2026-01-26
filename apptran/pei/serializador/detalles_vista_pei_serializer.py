# serializers.py
from rest_framework import serializers
from spme_estructuracion_pei.models import (
    Pei, 
    ObjetivoPei, 
    FactoresCriticos, 
    IndicadorPeiCuantitativo, 
    IndicadorPeiCualitativo, 
    ActividadPei
    )

class FactoresCriticosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresCriticos
        fields = ['id', 'factor_critico']

class IndicadorPeiCuantitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCuantitativo
        fields = ['id', 'codigo', 'descripcion', 'tipo', 'numerador', 'denominador', 
                  'umbral_des_literal_um1', 'umbral_des_literal_um2', 'umbral_des_literal_um3']

class IndicadorPeiCualitativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorPeiCualitativo
        fields = ['id', 'codigo', 'descripcion', 'tipo', 
                  'umbral_des_literal_um1', 'umbral_des_literal_um2', 'umbral_des_literal_um3']

class ObjetivoPeiSerializer(serializers.ModelSerializer):
    factores_criticos = FactoresCriticosSerializer(many=True, read_only=True)
    indicadores_cuantitativos = serializers.SerializerMethodField()
    indicadores_cualitativos = serializers.SerializerMethodField()
    total_indicadores = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjetivoPei
        fields = ['id', 'codigo', 'descripcion', 'factores_criticos', 
                  'indicadores_cuantitativos', 'indicadores_cualitativos', 'total_indicadores']
    
    def get_indicadores_cuantitativos(self, obj):
        indicadores = obj.indicador_pei_objetivo.filter(tipo='CUANTITATIVO')
        return IndicadorPeiCuantitativoSerializer(indicadores, many=True).data
    
    def get_indicadores_cualitativos(self, obj):
        indicadores = obj.indicador_pei_objetivo.filter(tipo='CUALITATIVO')
        return IndicadorPeiCualitativoSerializer(indicadores, many=True).data
    
    def get_total_indicadores(self, obj):
        return obj.indicador_pei_objetivo.count()

class ActividadPeiResumenSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)
    total_tareas = serializers.SerializerMethodField()
    
    class Meta:
        model = ActividadPei
        fields = ['id', 'codigo', 'nombreCorto', 'descripcion', 'estado', 
                  'fecha_inicio', 'fecha_cierre', 'presupuesto', 
                  'presupuestoGlobal', 'totalEjecutado', 'saldo', 
                  'responsable_nombre', 'total_tareas']
    
    def get_total_tareas(self, obj):
        return obj.tareas_pei.count()

class PeiDetalleSerializer(serializers.ModelSerializer):
    objetivos = ObjetivoPeiSerializer(source='pei_obj_general', many=True, read_only=True)
    actividades = serializers.SerializerMethodField()
    estadisticas = serializers.SerializerMethodField()
    resumen_financiero = serializers.SerializerMethodField()
    total_objetivos = serializers.SerializerMethodField()
    total_actividades = serializers.SerializerMethodField()
    total_indicadores = serializers.SerializerMethodField()
    vigencia = serializers.SerializerMethodField()
    
    class Meta:
        model = Pei
        fields = ['id', 'titulo', 'descripcion', 'fecha_creacion', 
                  'fecha_inicio', 'fecha_fin', 'esta_vigente',
                  'objetivos', 'actividades', 'estadisticas',
                  'resumen_financiero', 'total_objetivos', 
                  'total_actividades', 'total_indicadores', 'vigencia']
    
    def get_actividades(self, obj):
        actividades = obj.actividad_pei.all()
        return ActividadPeiResumenSerializer(actividades, many=True).data
    
    def get_estadisticas(self, obj):
        actividades = obj.actividad_pei.all()
        
        return {
            'actividades_por_estado': {
                'creadas': actividades.filter(estado='CRD').count(),
                'planificadas': actividades.filter(estado='PLAN').count(),
                'en_ejecucion': actividades.filter(estado='EJEC').count(),
                'en_reporte': actividades.filter(estado='REP').count(),
                'finalizadas': actividades.filter(estado='FIN').count(),
                'retrasadas': actividades.filter(estado='RETR').count(),
                'reprogramadas': actividades.filter(estado='REPROG').count(),
            },
            'actividades_inactivas': actividades.filter(estaInactiva=True).count(),
            'tareas_totales': sum(act.tareas_pei.count() for act in actividades),
        }
    
    def get_resumen_financiero(self, obj):
        actividades = obj.actividad_pei.all()
        total_presupuesto = sum(act.presupuesto or 0 for act in actividades)
        total_ejecutado = sum(act.totalEjecutado or 0 for act in actividades)
        total_saldo = sum(act.saldo or 0 for act in actividades)
        
        return {
            'presupuesto_total': total_presupuesto,
            'ejecutado_total': total_ejecutado,
            'saldo_total': total_saldo,
            'porcentaje_ejecucion': (total_ejecutado / total_presupuesto * 100) if total_presupuesto > 0 else 0,
        }
    
    def get_total_objetivos(self, obj):
        return obj.pei_obj_general.count()
    
    def get_total_actividades(self, obj):
        return obj.actividad_pei.count()
    
    def get_total_indicadores(self, obj):
        total = 0
        for objetivo in obj.pei_obj_general.all():
            total += objetivo.indicador_pei_objetivo.count()
        return total
    
    def get_vigencia(self, obj):
        from django.utils import timezone
        hoy = timezone.now().date()
        
        if obj.fecha_inicio and obj.fecha_fin:
            if obj.fecha_inicio <= hoy <= obj.fecha_fin:
                return 'VIGENTE'
            elif hoy < obj.fecha_inicio:
                return 'PENDIENTE'
            else:
                return 'VENCIDO'
        return 'NO DEFINIDA'
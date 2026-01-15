# serializers.py
from rest_framework import serializers
from spme_planificacion.models import PlanificacionPei

class SeguimientoPeiSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    actualizado_por_nombre = serializers.CharField(source='actualizado_por.get_full_name', read_only=True)
    
    # Agregar campo formateado para mejor visualización
    creado_el_formatted = serializers.SerializerMethodField()
    actualizado_el_formatted = serializers.SerializerMethodField()
    
    # Calcular días desde creación
    dias_desde_creacion = serializers.SerializerMethodField()
    
    class Meta:
        model = PlanificacionPei
        fields = '__all__'
    
    def get_creado_el_formatted(self, obj):
        """Formatear fecha de creación para mejor visualización"""
        if obj.creado_el:
            return obj.creado_el.strftime('%d/%m/%Y %H:%M')
        return None
    
    def get_actualizado_el_formatted(self, obj):
        """Formatear fecha de actualización para mejor visualización"""
        if obj.actualizado_el:
            return obj.actualizado_el.strftime('%d/%m/%Y %H:%M')
        return None
    
    def get_dias_desde_creacion(self, obj):
        """Calcular días transcurridos desde la creación"""
        from django.utils import timezone
        if obj.creado_el:
            delta = timezone.now() - obj.creado_el
            return delta.days
        return None
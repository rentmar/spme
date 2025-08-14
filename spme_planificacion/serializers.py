from rest_framework import serializers
from .models import ProyectoPlan, PlanRevision


class PlanRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanRevision
        fields = '__all__'
        read_only_fields = ('modificado_el', 'plan')


class ProyectoPlanSerializer(serializers.ModelSerializer):
    revisiones = PlanRevisionSerializer(many=True, read_only=True)
    class Meta:
        model = ProyectoPlan
        fields = '__all__'
        read_only_fields = ('version', 'creado', 'actualizado')


class ProyectoPlanDetailSerializer(serializers.ModelSerializer):
    revisiones = serializers.SerializerMethodField()  
    class Meta:
        model = ProyectoPlan
        fields = ['id', 'table_config', 'rows_data', 'version', 'creado', 'actualizado', 'proyecto', 'revisiones']
        read_only_fields = fields
    
    def get_revisiones(self, obj):
        # Obtiene solo las revisiones de esta versión específica
        revisions = obj.revisiones.filter(version=obj.version).order_by('-modificado_el')
        return PlanRevisionSerializer(revisions, many=True).data



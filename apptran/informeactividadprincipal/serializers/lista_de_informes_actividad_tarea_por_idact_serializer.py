# serializers.py
from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import InformeActividadPrincipal, InformeTareaPrincipal


class InformeTareaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeTareaPrincipal
        fields = '__all__'

class InformeActividadPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeActividadPrincipal
        fields = '__all__'

class TareaActividadSerializer(serializers.ModelSerializer):
    # Incluye los informes relacionados con cada tarea
    informes_tarea = serializers.SerializerMethodField()
    
    class Meta:
        model = TareaActividad
        fields = '__all__'
    
    def get_informes_tarea(self, obj):
        # Obtiene todos los informes relacionados con esta tarea
        informes = InformeTareaPrincipal.objects.filter(tarea=obj)
        return InformeTareaPrincipalSerializer(informes, many=True).data

class ActividadDetalladaSerializer(serializers.ModelSerializer):
    # Incluye las tareas relacionadas
    tareas = serializers.SerializerMethodField()
    
    # Incluye los informes directos de la actividad
    informes_actividad = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = '__all__'
    
    def get_tareas(self, obj):
        # Obtiene todas las tareas relacionadas con esta actividad
        tareas = TareaActividad.objects.filter(actividad=obj)
        return TareaActividadSerializer(tareas, many=True).data
    
    def get_informes_actividad(self, obj):
        # Obtiene todos los informes relacionados directamente con esta actividad
        informes = InformeActividadPrincipal.objects.filter(actividad=obj)
        return InformeActividadPrincipalSerializer(informes, many=True).data
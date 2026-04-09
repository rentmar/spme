# Serializer
from rest_framework import serializers
from django.core.exceptions import ValidationError

from spme_autenticacion.models import Usuario
from spme_monitoreo.models import (
    InformeActividadPrincipal, 
    SolicitudViaje
    )
from spme_monitoreo.modelos_vinculaciones import VinculacionSolicitudInforme

# from ..modelos_vinculaciones import VinculacionSolicitudInforme
# from solicitudes_viaje.models import SolicitudViaje
# from ..models import InformeActividadPrincipal
# from ..models import Usuario  


class SolicitudViajeVinculadaSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar solicitudes de viaje con información de vinculación.
    """
    
    estado_validacion = serializers.SerializerMethodField()
    fecha_vinculacion = serializers.SerializerMethodField()
    puede_vincularse = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudViaje
        fields = '__all__'
    
    def get_estado_validacion(self, obj):
        if obj.validacionCoordinador:
            return 'aprobada'
        elif obj.validacionResponsable:
            return 'validada_responsable'
        else:
            return 'pendiente'
    
    def get_fecha_vinculacion(self, obj):
        vinculacion = obj.vinculaciones_informe.filter(activa=True).first()
        return vinculacion.fecha_vinculacion if vinculacion else None
    
    def get_puede_vincularse(self, obj):
        tiene_vinculacion_activa = obj.vinculaciones_informe.filter(activa=True).exists()
        esta_aprobada = obj.validacionCoordinador
        return not tiene_vinculacion_activa and esta_aprobada


class VinculacionSolicitudInformeSerializer(serializers.ModelSerializer):
    """
    Serializer para gestionar vinculaciones.
    """
    
    solicitud_detalle = SolicitudViajeVinculadaSerializer(
        source='solicitud',
        read_only=True
    )
    
    informe_numero = serializers.CharField(
        source='informe.numeroInforme',
        read_only=True
    )
    
    informe_actividad_codigo = serializers.SerializerMethodField()
    
    # Campos para mostrar información del usuario que realizó la vinculación
    usuario_nombre = serializers.SerializerMethodField()
    usuario_username = serializers.CharField(
        source='usuario_vinculo.username',
        read_only=True,
        default=None
    )
    
    class Meta:
        model = VinculacionSolicitudInforme
        fields = [
            'id',
            'solicitud',
            'solicitud_detalle',
            'informe',
            'informe_numero',
            'informe_actividad_codigo',
            'fecha_vinculacion',
            'usuario_vinculo',
            'usuario_nombre',
            'usuario_username',
            'activa',
            'observaciones'
        ]
        read_only_fields = ['fecha_vinculacion', 'usuario_vinculo']
    
    def get_informe_actividad_codigo(self, obj):
        if obj.informe and obj.informe.actividad:
            return obj.informe.actividad.codigo
        return None
    
    def get_usuario_nombre(self, obj):
        """
        Obtiene el nombre completo del usuario usando el método get_full_name()
        del modelo Usuario personalizado.
        """
        if obj.usuario_vinculo:
            return obj.usuario_vinculo.get_full_name()
        return 'Sistema'
    
    def validate(self, data):
        solicitud = data.get('solicitud')
        informe = data.get('informe')
        
        if solicitud and not solicitud.validacionCoordinador:
            raise serializers.ValidationError({
                'solicitud': 'La solicitud debe estar aprobada por el coordinador para vincularse.'
            })
        
        if solicitud and informe and solicitud.actividad != informe.actividad:
            raise serializers.ValidationError({
                'actividad': 'La solicitud y el informe deben pertenecer a la misma actividad.'
            })
        
        return data


class VincularSolicitudSerializer(serializers.Serializer):
    """
    Serializer para la acción específica de vincular.
    """
    
    solicitud_id = serializers.IntegerField()
    informe_id = serializers.IntegerField()
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_solicitud_id(self, value):
        try:
            solicitud = SolicitudViaje.objects.get(id=value)
        except SolicitudViaje.DoesNotExist:
            raise serializers.ValidationError("La solicitud de viaje no existe.")
        
        if not solicitud.validacionCoordinador:
            raise serializers.ValidationError(
                "La solicitud debe estar aprobada por el coordinador para vincularse."
            )
        
        vinculacion_activa = solicitud.vinculaciones_informe.filter(activa=True).first()
        if vinculacion_activa:
            raise serializers.ValidationError(
                f"La solicitud {solicitud.numeroFormulario} ya está vinculada "
                f"al informe {vinculacion_activa.informe.numeroInforme}."
            )
        
        return value
    
    def validate_informe_id(self, value):
        try:
            informe = InformeActividadPrincipal.objects.get(id=value)
        except InformeActividadPrincipal.DoesNotExist:
            raise serializers.ValidationError("El informe de actividad no existe.")
        return value
    
    def validate(self, data):
        solicitud_id = data.get('solicitud_id')
        informe_id = data.get('informe_id')
        
        if solicitud_id and informe_id:
            solicitud = SolicitudViaje.objects.get(id=solicitud_id)
            informe = InformeActividadPrincipal.objects.get(id=informe_id)
            
            if solicitud.actividad != informe.actividad:
                raise serializers.ValidationError({
                    'actividad': 'La solicitud y el informe deben pertenecer a la misma actividad.'
                })
        
        return data


class DesvincularSolicitudSerializer(serializers.Serializer):
    """Serializer para la acción de desvincular"""
    
    solicitud_id = serializers.IntegerField()
    informe_id = serializers.IntegerField()
    
    def validate(self, data):
        solicitud_id = data.get('solicitud_id')
        informe_id = data.get('informe_id')
        
        try:
            vinculacion = VinculacionSolicitudInforme.objects.get(
                solicitud_id=solicitud_id,
                informe_id=informe_id,
                activa=True
            )
            data['vinculacion'] = vinculacion
        except VinculacionSolicitudInforme.DoesNotExist:
            raise serializers.ValidationError(
                "No existe una vinculación activa entre estos documentos."
            )
        
        return data
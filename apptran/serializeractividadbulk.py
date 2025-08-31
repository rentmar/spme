# serializers.py
from rest_framework import serializers
# from .models import Actividad, TipoActividad, Usuario, Proyecto
from spme_actividades.models import Actividad, TipoActividad
from spme_autenticacion.models import Usuario
from spme_estructuracion_proyecto.models import Proyecto
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime

class ActividadBulkSerializer(serializers.ModelSerializer):
    # Campos para procesamiento (opcionales)
    tipo_str = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    responsable_str = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    proyecto_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Sobrescribir campos de fecha para hacerlos más flexibles
    fecha_inicio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_cierre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_programada = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'tipo_str', 'proceso', 'resultado_og', 'resultado_oe', 
            'producto_oe', 'objetivo_pei', 'indicador_pei', 'proyecto_id', 'responsable_str', 'rutaTrazadoIndicadores', 'factoresCriticos',
        ]
        extra_kwargs = {
            'id': {'required': False}
        }
    
    def to_internal_value(self, data):
        """
        Convierte los formatos de fecha antes de la validación estándar
        """
        # Hacer una copia para no modificar el original
        data = data.copy()
        
        # Convertir formatos de fecha
        date_fields = ['fecha_inicio', 'fecha_cierre', 'fecha_programada']
        for field in date_fields:
            if field in data and data[field] and isinstance(data[field], str) and '/' in data[field]:
                try:
                    data[field] = datetime.strptime(data[field], '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    # Dejar la fecha como está para que falle la validación posterior
                    pass
        
        # Mapear campos del formato recibido al formato del serializer
        if 'proyecto' in data:
            data['proyecto_id'] = data.pop('proyecto', None)
        
        if 'responsable' in data:
            data['responsable_str'] = data.pop('responsable', None)
        
        if 'tipo' in data:
            data['tipo_str'] = data.pop('tipo', None)
        
        return super().to_internal_value(data)
    
    def validate_tipo_str(self, value):
        """Valida y obtiene el tipo de actividad desde el string"""
        if value:
            # Extraer la sigla del string (ej: "ACAP - Actividad de Capacitación" -> "ACAP")
            sigla = value.split(' - ')[0].strip() if ' - ' in value else value.strip()
            try:
                tipo = TipoActividad.objects.get(sigla=sigla)
                return tipo
            except TipoActividad.DoesNotExist:
                # Intentar buscar por nombre completo
                try:
                    tipo = TipoActividad.objects.get(tipo_actividad__icontains=value)
                    return tipo
                except (TipoActividad.DoesNotExist, TipoActividad.MultipleObjectsReturned):
                    raise serializers.ValidationError(f"Tipo de actividad no encontrado: {value}")
        return None
    
    def validate_responsable_str(self, value):
        """Valida y obtiene el usuario responsable desde el username"""
        if value:
            try:
                usuario = Usuario.objects.get(username=value)
                return usuario
            except Usuario.DoesNotExist:
                raise serializers.ValidationError(f"Usuario no encontrado: {value}")
        return None
    
    def validate_proyecto_id(self, value):
        """Valida que el proyecto exista"""
        if value:
            try:
                proyecto = Proyecto.objects.get(id=value)
                return proyecto
            except Proyecto.DoesNotExist:
                raise serializers.ValidationError(f"Proyecto no encontrado: {value}")
        return None
    
    def validate(self, data):
        """Validación adicional para campos opcionales"""
        # Si no viene proyecto_id en los datos, intentar obtenerlo de otras fuentes
        if 'proyecto_id' not in data:
            proyecto_id = self.initial_data.get('proyecto')
            if proyecto_id:
                try:
                    data['proyecto_id'] = Proyecto.objects.get(id=proyecto_id)
                except (Proyecto.DoesNotExist, ValueError):
                    # Si no se puede encontrar, dejar como None
                    data['proyecto_id'] = None
        
        # Misma lógica para responsable
        if 'responsable_str' not in data:
            responsable_str = self.initial_data.get('responsable')
            if responsable_str:
                try:
                    data['responsable_str'] = Usuario.objects.get(username=responsable_str)
                except Usuario.DoesNotExist:
                    # Si no se puede encontrar, dejar como None
                    data['responsable_str'] = None
        
        return data
    
    def create(self, validated_data):
        """Crear una nueva actividad"""
        # Extraer campos especiales
        tipo = validated_data.pop('tipo_str', None)
        responsable = validated_data.pop('responsable_str', None)
        proyecto = validated_data.pop('proyecto_id', None)
        
        # Crear la actividad
        actividad = Actividad.objects.create(
            tipo=tipo,
            responsable=responsable,
            proyecto=proyecto,
            **validated_data
        )
        return actividad
    
    def update(self, instance, validated_data):
        """Actualizar una actividad existente"""
        # Extraer campos especiales
        tipo = validated_data.pop('tipo_str', None)
        responsable = validated_data.pop('responsable_str', None)
        proyecto = validated_data.pop('proyecto_id', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar relaciones si se proporcionaron
        if tipo is not None:
            instance.tipo = tipo
        if responsable is not None:
            instance.responsable = responsable
        if proyecto is not None:
            instance.proyecto = proyecto
        
        instance.save()
        return instance
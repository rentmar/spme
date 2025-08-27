# serializers.py 
from rest_framework import serializers
from spme_actividades.models import Actividad, TipoActividad
from spme_autenticacion.models import Usuario
from spme_estructuracion_proyecto.models import Proyecto
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime
import json

class ActividadBulkSerializer(serializers.ModelSerializer):
    # Campos para procesamiento (opcionales)
    tipo_str = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    responsable_str = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    proyecto_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Sobrescribir campos de fecha para hacerlos más flexibles
    fecha_inicio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_cierre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_programada = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Campos para relaciones adicionales
    resultado_oe_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    producto_oe_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    objetivo_pei_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    indicador_pei_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    proceso_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre',
            'presupuesto', 'presupuestoGlobal', 'totalReportado', 
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'tipo_str', 'proceso_id', 'resultado_oe_id', 'producto_oe_id', 
            'objetivo_pei_id', 'indicador_pei_id', 'proyecto_id', 'responsable_str',
            'rutaTrazadoIndicadores'
        ]
        extra_kwargs = {
            'id': {'required': False},
            'rutaTrazadoIndicadores': {'required': False, 'allow_null': True}
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
        field_mappings = {
            'proyecto': 'proyecto_id',
            'responsable': 'responsable_str',
            'tipo': 'tipo_str',
            'resultado_oe': 'resultado_oe_id',
            'producto_oe': 'producto_oe_id',
            'objetivo_pei': 'objetivo_pei_id',
            'indicador_pei': 'indicador_pei_id',
            'proceso': 'proceso_id'
        }
        
        for source_field, target_field in field_mappings.items():
            if source_field in data:
                data[target_field] = data.pop(source_field, None)
        
        # Procesar rutaTrazadoIndicadores si es string JSON
        if 'rutaTrazadoIndicadores' in data and isinstance(data['rutaTrazadoIndicadores'], str):
            try:
                data['rutaTrazadoIndicadores'] = json.loads(data['rutaTrazadoIndicadores'])
            except (json.JSONDecodeError, TypeError):
                data['rutaTrazadoIndicadores'] = None
        
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
        resultado_oe = validated_data.pop('resultado_oe_id', None)
        producto_oe = validated_data.pop('producto_oe_id', None)
        objetivo_pei = validated_data.pop('objetivo_pei_id', None)
        indicador_pei = validated_data.pop('indicador_pei_id', None)
        proceso = validated_data.pop('proceso_id', None)
        
        # Crear la actividad
        actividad = Actividad.objects.create(
            tipo=tipo,
            responsable=responsable,
            proyecto=proyecto,
            resultado_oe_id=resultado_oe,
            producto_oe_id=producto_oe,
            objetivo_pei_id=objetivo_pei,
            indicador_pei_id=indicador_pei,
            proceso_id=proceso,
            **validated_data
        )
        return actividad
    
    def update(self, instance, validated_data):
        """Actualizar una actividad existente"""
        # Extraer campos especiales
        tipo = validated_data.pop('tipo_str', None)
        responsable = validated_data.pop('responsable_str', None)
        proyecto = validated_data.pop('proyecto_id', None)
        resultado_oe = validated_data.pop('resultado_oe_id', None)
        producto_oe = validated_data.pop('producto_oe_id', None)
        objetivo_pei = validated_data.pop('objetivo_pei_id', None)
        indicador_pei = validated_data.pop('indicador_pei_id', None)
        proceso = validated_data.pop('proceso_id', None)
        
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
        if resultado_oe is not None:
            instance.resultado_oe_id = resultado_oe
        if producto_oe is not None:
            instance.producto_oe_id = producto_oe
        if objetivo_pei is not None:
            instance.objetivo_pei_id = objetivo_pei
        if indicador_pei is not None:
            instance.indicador_pei_id = indicador_pei
        if proceso is not None:
            instance.proceso_id = proceso
        
        instance.save()
        return instance
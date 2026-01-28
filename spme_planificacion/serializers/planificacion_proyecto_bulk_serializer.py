# serializers.py 
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

# from .models import Actividad, Usuario, TipoActividad, Proyecto
# from .models import Proceso, ResultadoOG, ResultadoOE, ProductoOE, ObjetivoPei, IndicadorPeiBase

from spme_actividades.models import (
    Actividad,
    TipoActividad,
)

from spme_estructuracion_proyecto.models import (
    Proceso, 
    ResultadoOG, 
    ResultadoOE, 
    ProductoOE, 
    Proyecto,
)

from spme_estructuracion_pei.models import (
    ObjetivoPei,
    IndicadorPeiBase,
)

from spme_autenticacion.models import Usuario

# serializers.py
# from .models import Actividad, TipoActividad, Usuario, Proyecto


# serializers.py (agregar al inicio del archivo)
class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializer específico para importar actividades desde JSON
    Acepta los datos en el formato original
    """
    # Campos write_only para relaciones
    tipo_codigo = serializers.CharField(write_only=True, required=False, allow_null=True)
    proyecto_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    responsable_username = serializers.CharField(write_only=True, required=False, allow_null=True)
    objetivo_pei_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    indicador_pei_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre', 'presupuesto', 'presupuestoGlobal',
            'totalReportado', 'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'tipo', 'proceso', 'resultado_og', 'resultado_oe', 'producto_oe',
            'objetivo_pei', 'indicador_pei', 'proyecto', 'responsable', 'rutaTrazadoIndicadores',
            'factoresCriticos', 'estructuraProcedencia', 'estaInactiva',
            'tipo_codigo', 'proyecto_id', 'responsable_username', 'objetivo_pei_id', 'indicador_pei_id'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, data):
        """
        Validación personalizada para manejar relaciones
        """
        # Extraer campos especiales
        tipo_codigo = data.pop('tipo_codigo', None)
        proyecto_id = data.pop('proyecto_id', None)
        responsable_username = data.pop('responsable_username', None)
        objetivo_pei_id = data.pop('objetivo_pei_id', None)
        indicador_pei_id = data.pop('indicador_pei_id', None)
        
        # Procesar tipo (si se recibió tipo_codigo)
        if tipo_codigo and not data.get('tipo'):
            tipo_actividad = self._get_or_create_tipo(tipo_codigo)
            if tipo_actividad:
                data['tipo'] = tipo_actividad
        
        # Procesar proyecto
        if proyecto_id and not data.get('proyecto'):
            try:
                data['proyecto'] = Proyecto.objects.get(id=proyecto_id)
            except Proyecto.DoesNotExist:
                raise ValidationError({'proyecto': f'Proyecto con id {proyecto_id} no existe'})
        
        # Procesar responsable
        if responsable_username and not data.get('responsable'):
            try:
                data['responsable'] = Usuario.objects.get(username=responsable_username)
            except Usuario.DoesNotExist:
                data['responsable'] = None
        
        # Procesar objetivo_pei
        if objetivo_pei_id and not data.get('objetivo_pei'):
            try:
                data['objetivo_pei'] = ObjetivoPei.objects.get(id=objetivo_pei_id)
            except ObjetivoPei.DoesNotExist:
                raise ValidationError({'objetivo_pei': f'Objetivo PEI con id {objetivo_pei_id} no existe'})
        
        # Procesar indicador_pei
        if indicador_pei_id and not data.get('indicador_pei'):
            try:
                data['indicador_pei'] = IndicadorPeiBase.objects.get(id=indicador_pei_id)
            except IndicadorPeiBase.DoesNotExist:
                raise ValidationError({'indicador_pei': f'Indicador PEI con id {indicador_pei_id} no existe'})
        
        return data
    
    def to_internal_value(self, data):
        """
        Convertir datos de entrada al formato esperado por el modelo
        """
        processed_data = {}
        
        for key, value in data.items():
            # Mapear campos de entrada a campos internos
            if key == 'tipo' and isinstance(value, str):
                processed_data['tipo_codigo'] = value
            elif key == 'proyecto':
                processed_data['proyecto_id'] = value
            elif key == 'responsable':
                processed_data['responsable_username'] = value
            elif key == 'objetivo_pei':
                processed_data['objetivo_pei_id'] = value
            elif key == 'indicador_pei':
                processed_data['indicador_pei_id'] = value
            else:
                processed_data[key] = value
        
        return super().to_internal_value(processed_data)
    
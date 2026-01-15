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


class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializer específico para importar actividades desde JSON
    Acepta los datos en el formato original
    """
    # NO usar list(model._meta.fields) - usar nombres explícitos
    tipo_codigo = serializers.CharField(write_only=True, required=False, allow_null=True)
    proyecto_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    responsable_username = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Actividad
        # Especificar campos EXPLÍCITAMENTE, no usar model._meta.fields
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 
            'riesgos', 'objetivo_de_actividad', 'descripcion_evaluacion',
            'descripcion_tipo_actividad', 'fecha_programada', 'fecha_inicio',
            'fecha_cierre', 'presupuesto', 'presupuestoGlobal', 'totalReportado',
            'totalEjecutado', 'saldo', 'gradoEjecucion', 'procedencia_fondos',
            'estado', 'tipo', 'proceso', 'resultado_og', 'resultado_oe',
            'producto_oe', 'objetivo_pei', 'indicador_pei', 'proyecto',
            'responsable', 'rutaTrazadoIndicadores', 'factoresCriticos',
            'estructuraProcedencia', 'estaInactiva',
            'tipo_codigo', 'proyecto_id', 'responsable_username'
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
                data['responsable'] = None  # O puedes asignar un usuario por defecto
        
        return data
    
    def _get_or_create_tipo(self, tipo_codigo):
        """Obtener o crear TipoActividad basado en código"""
        if not tipo_codigo:
            return None
        
        try:
            return TipoActividad.objects.get(codigo=tipo_codigo)
        except TipoActividad.DoesNotExist:
            # Crear nuevo tipo
            nombres = {
                'NODEF': 'No definido',
                'ACAP': 'Actividad de Capacitación',
                'PRIN': 'Proyecto de Investigación',
                'AOP': 'Actividad Operativa',
                'CSNS': 'Campaña de Sensibilización',
                'PDES': 'Proyecto de Desarrollo',
                'AINC': 'Actividad de Incidencia',
                'AART': 'Actividad de Articulación',
                'OTRO': 'Otro',
            }
            
            nombre = nombres.get(tipo_codigo, tipo_codigo)
            
            return TipoActividad.objects.create(
                codigo=tipo_codigo,
                nombre=nombre
            )
    
    def to_internal_value(self, data):
        """
        Convertir datos de entrada al formato esperado por el modelo
        """
        # Hacer copia para no modificar original
        processed_data = {}
        
        for key, value in data.items():
            if key == 'tipo' and isinstance(value, str):
                # Convertir 'tipo': 'ACAP' -> 'tipo_codigo': 'ACAP'
                processed_data['tipo_codigo'] = value
            elif key == 'proyecto':
                processed_data['proyecto_id'] = value
            elif key == 'responsable':
                processed_data['responsable_username'] = value
            else:
                processed_data[key] = value
        
        return super().to_internal_value(processed_data)
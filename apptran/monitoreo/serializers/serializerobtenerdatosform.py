# serializers.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad
from spme_monitoreo.models import FormaPago

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'paterno', 'materno', 'cargo', 'ci', 'banco', 'permisos', 'correo']

class ValidadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'paterno', 'materno', 'cargo', 'correo', 'ci']

class ActividadSerializer(serializers.ModelSerializer):
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField(source='fecha_cierre') 
    
    class Meta:
        model = Actividad
        fields = '__all__'

class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = '__all__'
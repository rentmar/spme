# spme/apptran/monitoreo/serializers/sol_pago_directo_form_validacion_serializer.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudPagoDirecto, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad


class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = ['id', 'codigo', 'formaPago']


class UsuarioBasicSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'paterno', 'materno', 'nombre_completo', 'cargo']

    def get_nombre_completo(self, obj):
        return obj.get_full_name()


class ActividadBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'


class TareaActividadBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'


class SolicitudPagoDirectoSerializer(serializers.ModelSerializer):
    forma_pago_info = FormaPagoSerializer(source='formaPago', read_only=True)
    contador_info = UsuarioBasicSerializer(source='contador', read_only=True)
    coordinador_info = UsuarioBasicSerializer(source='coordinador', read_only=True)
    usuario_info = UsuarioBasicSerializer(source='usuario', read_only=True)
    actividad_info = ActividadBasicSerializer(source='actividad', read_only=True)
    tarea_info = TareaActividadBasicSerializer(source='tarea', read_only=True)

    class Meta:
        model = SolicitudPagoDirecto
        fields = '__all__'
# serializers.py
from rest_framework import serializers
# from .models import SolicitudFondos, FormaPago, Usuario, Actividad, TareaActividad
from spme_monitoreo.models import SolicitudFondos, FormaPago
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

class SolicitudFondosSerializer(serializers.ModelSerializer):
    forma_pago_info = FormaPagoSerializer(source='formaPago', read_only=True)
    responsable_info = UsuarioBasicSerializer(source='responsable', read_only=True)
    coordinador_info = UsuarioBasicSerializer(source='coordinador', read_only=True)
    usuario_info = UsuarioBasicSerializer(source='usuario', read_only=True)
    actividad_info = ActividadBasicSerializer(source='actividad', read_only=True)
    tarea_info = TareaActividadBasicSerializer(source='tarea', read_only=True)
    
    class Meta:
        model = SolicitudFondos
        fields = '__all__'

class SolicitudFondosCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = [
            'numeroFormulario', 'detalleDestinoFondos', 'formaPago',
            'lugarSolicitud', 'fechaSolicitud', 'montoSolicitado',
            'usuario', 'actividad', 'tarea'
        ]

class SolicitudFondosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = [
            'detalleDestinoFondos', 'formaPago', 'lugarSolicitud',
            'fechaSolicitud', 'montoSolicitado', 'actividad', 'tarea'
        ]

class SolicitudFondosValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = ['validacionResponsable', 'validacionCoordinador']
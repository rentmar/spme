# serializers.py
from rest_framework import serializers
#from .models import SolicitudViaje, FormaPago, Usuario, Actividad, TareaActividad
from spme_monitoreo.models import SolicitudViaje, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad

class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = ['id', 'codigo', 'formaPago']

class UsuarioInfoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'paterno', 'materno', 'nombre_completo', 'cargo']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()

class ActividadInfoSerializer(serializers.ModelSerializer):
    tipo = serializers.PrimaryKeyRelatedField(read_only=True)
    proceso = serializers.PrimaryKeyRelatedField(read_only=True)
    resultado_og = serializers.PrimaryKeyRelatedField(read_only=True)
    resultado_oe = serializers.PrimaryKeyRelatedField(read_only=True)
    producto_oe = serializers.PrimaryKeyRelatedField(read_only=True)
    objetivo_pei = serializers.PrimaryKeyRelatedField(read_only=True)
    indicador_pei = serializers.PrimaryKeyRelatedField(read_only=True)
    proyecto = serializers.PrimaryKeyRelatedField(read_only=True)
    responsable = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'codigo', 'nombreCorto', 'descripcion', 'supuestos', 'riesgos',
            'objetivo_de_actividad', 'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'fecha_programada', 'fecha_inicio', 'fecha_cierre', 'presupuesto',
            'presupuestoGlobal', 'totalReportado', 'totalEjecutado', 'saldo',
            'gradoEjecucion', 'procedencia_fondos', 'estado', 'rutaTrazadoIndicadores',
            'tipo', 'proceso', 'resultado_og', 'resultado_oe', 'producto_oe',
            'objetivo_pei', 'indicador_pei', 'proyecto', 'responsable'
        ]

class TareaInfoSerializer(serializers.ModelSerializer):
    actividad = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = TareaActividad
        fields = [
            'id', 'estado', 'titulo', 'descripcion', 'fecha_creacion',
            'fecha_limite', 'presupuesto', 'actividad'
        ]

class SolicitudViajeSerializer(serializers.ModelSerializer):
    forma_pago_info = FormaPagoSerializer(source='formaPago', read_only=True)
    responsable_info = UsuarioInfoSerializer(source='responsable', read_only=True)
    coordinador_info = UsuarioInfoSerializer(source='coordinador', read_only=True)
    usuario_info = UsuarioInfoSerializer(source='usuario', read_only=True)
    actividad_info = ActividadInfoSerializer(source='actividad', read_only=True)
    tarea_info = TareaInfoSerializer(source='tarea', read_only=True)
    
    class Meta:
        model = SolicitudViaje
        fields = [
            'id', 'numeroFormulario', 'evento', 'fechaInicio', 'fechaFin',
            'lugarEvento', 'institucionesParticipantes', 'organizador',
            'quienCubreGastos', 'justificacionAsistencia', 'fondosUnitas',
            'tareasPrevias', 'montoSolicitado', 'lugarSolicitud', 'fechaSolicitud',
            'validacionResponsable', 'validacionCoordinador',
            'formaPago', 'responsable', 'coordinador', 'usuario', 'actividad', 'tarea',
            'forma_pago_info', 'responsable_info', 'coordinador_info', 
            'usuario_info', 'actividad_info', 'tarea_info'
        ]
from rest_framework import serializers
from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from spme_estructuracion_proyecto.models import Proyecto

#Datos del Proyecto
class ProyectoSerial(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = "__all__"

#Datos del Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'paterno']

#Tarea
class TareaActividadSer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'

#Datos de forma de pago
class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = '__all__'

#Serializar la actividad
class ActividadSerializer(serializers.ModelSerializer):
    responsable = UsuarioSerializer()
    proyecto = ProyectoSerial()
    class Meta:
        model = Actividad
        fields = '__all__'

class SolicitudFondosSerializers(serializers.ModelSerializer):
    responsable = UsuarioSerializer()
    coordinador = UsuarioSerializer()
    formaPago = FormaPagoSerializer()
    usuario = UsuarioSerializer()
    actividad = ActividadSerializer()
    tarea = TareaActividadSer()
    class Meta:
        model =  SolicitudFondos
        fields = '__all__'
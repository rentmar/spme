from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import *

from rest_framework import serializers
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import *

class TareaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaActividad
        fields = '__all__'

class SolicitudFondosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = '__all__'

# La clase SolicitudReembolsoSerializer ha sido eliminada.

class SolicitudPagoDirectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirecto
        fields = '__all__'

class SolicitudViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudViaje
        fields = '__all__'

class RendicionCuentasSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentas
        fields = '__all__'

class InformeActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformeActividad
        fields = '__all__'

class ActividadReporteSerializer(serializers.ModelSerializer):
    tareas = TareaActividadSerializer(many=True, read_only=True)
    solicitud_fondos = SolicitudFondosSerializer(many=True, read_only=True, source='usuario_actividad_solicitud')
    # El campo 'solicitud_reembolso' ha sido eliminado.
    solicitud_pago_directo = SolicitudPagoDirectoSerializer(many=True, read_only=True, source='usuario_actividad_sol_pago_directo')
    solicitud_viaje = SolicitudViajeSerializer(many=True, read_only=True, source='usuario_actividad_sol_viaje')
    rendicion_cuentas = RendicionCuentasSerializer(many=True, read_only=True, source='rendicion_cuentas_actividad')
    informe_actividad = InformeActividadSerializer(many=True, read_only=True, source='actividad_informe_actividad')
    
    class Meta:
        model = Actividad
        fields = '__all__'

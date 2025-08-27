# serializers.py
from rest_framework import serializers
from spme_monitoreo.models import SolicitudViaje, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad

class SolicitudViajeCreateSerializer(serializers.ModelSerializer):
    forma_pago = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(), 
        source='formaPago',
        required=False,
        allow_null=True
    )
    id_responsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='responsable',
        required=False,
        allow_null=True
    )
    id_coordinador = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='coordinador',
        required=False,
        allow_null=True
    )
    id_usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='usuario',
        required=False,
        allow_null=True
    )
    id_actividad = serializers.PrimaryKeyRelatedField(
        queryset=Actividad.objects.all(),
        source='actividad',
        required=False,
        allow_null=True
    )
    id_tarea = serializers.PrimaryKeyRelatedField(
        queryset=TareaActividad.objects.all(),
        source='tarea',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = SolicitudViaje
        fields = [
            'numeroFormulario', 'evento', 'fechaInicio', 'fechaFin',
            'lugarEvento', 'institucionesParticipantes', 'organizador',
            'quienCubreGastos', 'justificacionAsistencia', 'fondosUnitas',
            'tareasPrevias', 'montoSolicitado', 'lugarSolicitud', 'fechaSolicitud',
            'validacionResponsable', 'validacionCoordinador',
            'forma_pago', 'id_responsable', 'id_coordinador', 
            'id_usuario', 'id_actividad', 'id_tarea'
        ]
        extra_kwargs = {
            'numeroFormulario': {'required': False, 'allow_null': True},
            'evento': {'required': False, 'allow_null': True},
            'fechaInicio': {'required': False, 'allow_null': True},
            'fechaFin': {'required': False, 'allow_null': True},
            'lugarEvento': {'required': False, 'allow_null': True},
            'institucionesParticipantes': {'required': False, 'allow_null': True},
            'organizador': {'required': False, 'allow_null': True},
            'quienCubreGastos': {'required': False, 'allow_null': True},
            'justificacionAsistencia': {'required': False, 'allow_null': True},
            'fondosUnitas': {'required': False, 'allow_null': True},
            'tareasPrevias': {'required': False, 'allow_null': True},
            'montoSolicitado': {'required': False, 'allow_null': True},
            'lugarSolicitud': {'required': False, 'allow_null': True},
            'fechaSolicitud': {'required': False, 'allow_null': True},
            'validacionResponsable': {'required': False},
            'validacionCoordinador': {'required': False},
        }
    
    def create(self, validated_data):
        # Generar número de formulario automáticamente si no se proporciona
        if not validated_data.get('numeroFormulario'):
            # Lógica para generar número de formulario único
            last_solicitud = SolicitudViaje.objects.order_by('-id').first()
            if last_solicitud and last_solicitud.numeroFormulario:
                try:
                    # Si ya existe un formato con "SF-", incrementamos el número
                    if last_solicitud.numeroFormulario.startswith('SF-'):
                        last_number = int(last_solicitud.numeroFormulario.replace('SF-', ''))
                        new_number = f"SF-{last_number + 1:04d}"
                    else:
                        # Si tiene otro formato, empezamos desde SF-0001
                        new_number = "SF-0001"
                except (ValueError, AttributeError):
                    new_number = "SF-0001"
            else:
                new_number = "SF-0001"
            validated_data['numeroFormulario'] = new_number
        
        return super().create(validated_data)
# serializers.py 
from rest_framework import serializers
#from .models import SolicitudFondos, FormaPago, Usuario, Actividad, TareaActividad
from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad


# serializers.py
from rest_framework import serializers
from django.db import transaction
from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad

class SolicitudFondosCreateSerializer(serializers.ModelSerializer):
    # Campos que vendrán en el JSON con nombres diferentes a los del modelo
    forma_pago = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(),
        source='formaPago'
    )
    lugar_solicitud = serializers.CharField(source='lugarSolicitud')
    fecha_solicitud = serializers.DateField(source='fechaSolicitud')
    monto_solicitado = serializers.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        source='montoSolicitado'
    )
    detalle_destino_fondos = serializers.JSONField(source='detalleDestinoFondos')
    validacion_responsable = serializers.BooleanField(source='validacionResponsable')
    validacion_coordinador = serializers.BooleanField(source='validacionCoordinador')
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
    
    # Cambiar el campo id_actividad para manejar el nuevo formato
    actividad = serializers.JSONField(write_only=True, required=False)
    
    id_tarea = serializers.PrimaryKeyRelatedField(
        queryset=TareaActividad.objects.all(),
        source='tarea',
        required=False,
        allow_null=True
    )

    class Meta:
        model = SolicitudFondos
        fields = [
            'detalle_destino_fondos', 'forma_pago', 'lugar_solicitud',
            'fecha_solicitud', 'monto_solicitado', 'validacion_responsable',
            'id_responsable', 'validacion_coordinador', 'id_coordinador',
            'id_usuario', 'actividad', 'id_tarea'
        ]

    @transaction.atomic
    def create(self, validated_data):
        # Extraer y procesar los datos de actividad si vienen en el nuevo formato
        actividad_data = validated_data.pop('actividad', None)
        actividad_obj = None
        
        # Si viene actividad en el nuevo formato, actualizar la actividad existente
        if actividad_data and 'id_actividad' in actividad_data:
            try:
                actividad_id = actividad_data['id_actividad']
                actividad_obj = Actividad.objects.select_for_update().get(id=actividad_id)
                
                # Actualizar los campos de descripción y objetivo si vienen en el JSON
                campos_actualizados = False
                if 'descripcion_actividad' in actividad_data:
                    actividad_obj.descripcion = actividad_data['descripcion_actividad']
                    campos_actualizados = True
                if 'objetivo_actividad' in actividad_data:
                    actividad_obj.objetivo_de_actividad = actividad_data['objetivo_actividad']
                    campos_actualizados = True
                
                if campos_actualizados:
                    actividad_obj.save()
                
                # Asignar la actividad actualizada a la solicitud de fondos
                validated_data['actividad'] = actividad_obj
                
            except Actividad.DoesNotExist:
                raise serializers.ValidationError(
                    {"actividad": f"La actividad con ID {actividad_id} no existe."}
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {"actividad": f"Error al actualizar la actividad: {str(e)}"}
                )
        
        # Generar número de formulario automáticamente si no viene
        if 'numeroFormulario' not in validated_data or not validated_data.get('numeroFormulario'):
            last_solicitud = SolicitudFondos.objects.order_by('-id').first()
            last_number = last_solicitud.id if last_solicitud else 0
            validated_data['numeroFormulario'] = f"SF-{last_number + 1:04d}"
        
        try:
            # Crear la solicitud de fondos dentro de la misma transacción
            solicitud = super().create(validated_data)
            return solicitud
            
        except Exception as e:
            # Si hay algún error al crear la solicitud, la transacción se revertirá
            # automáticamente incluyendo cualquier cambio en la actividad
            raise serializers.ValidationError(
                {"solicitud": f"Error al crear la solicitud de fondos: {str(e)}"}
            )



# class SolicitudFondosCreateSerializer(serializers.ModelSerializer):
#     # Campos que vendrán en el JSON con nombres diferentes a los del modelo
#     forma_pago = serializers.PrimaryKeyRelatedField(
#         queryset=FormaPago.objects.all(),
#         source='formaPago'
#     )
#     lugar_solicitud = serializers.CharField(source='lugarSolicitud')
#     fecha_solicitud = serializers.DateField(source='fechaSolicitud')
#     monto_solicitado = serializers.DecimalField(
#         max_digits=6, 
#         decimal_places=2, 
#         source='montoSolicitado'
#     )
#     detalle_destino_fondos = serializers.JSONField(source='detalleDestinoFondos')
#     validacion_responsable = serializers.BooleanField(source='validacionResponsable')
#     validacion_coordinador = serializers.BooleanField(source='validacionCoordinador')
#     id_responsable = serializers.PrimaryKeyRelatedField(
#         queryset=Usuario.objects.all(), 
#         source='responsable',
#         required=False,
#         allow_null=True
#     )
#     id_coordinador = serializers.PrimaryKeyRelatedField(
#         queryset=Usuario.objects.all(),
#         source='coordinador',
#         required=False,
#         allow_null=True
#     )
#     id_usuario = serializers.PrimaryKeyRelatedField(
#         queryset=Usuario.objects.all(),
#         source='usuario',
#         required=False,
#         allow_null=True
#     )
#     id_actividad = serializers.PrimaryKeyRelatedField(
#         queryset=Actividad.objects.all(),
#         source='actividad',
#         required=False,
#         allow_null=True
#     )
#     id_tarea = serializers.PrimaryKeyRelatedField(
#         queryset=TareaActividad.objects.all(),
#         source='tarea',
#         required=False,
#         allow_null=True
#     )

#     class Meta:
#         model = SolicitudFondos
#         fields = [
#             'detalle_destino_fondos', 'forma_pago', 'lugar_solicitud',
#             'fecha_solicitud', 'monto_solicitado', 'validacion_responsable',
#             'id_responsable', 'validacion_coordinador', 'id_coordinador',
#             'id_usuario', 'id_actividad', 'id_tarea'
#         ]

#     def create(self, validated_data):
#         # Generar número de formulario automáticamente si no viene
#         if 'numeroFormulario' not in validated_data or not validated_data.get('numeroFormulario'):
#             # Lógica para generar número de formulario (puedes personalizar esto)
#             last_solicitud = SolicitudFondos.objects.order_by('-id').first()
#             last_number = last_solicitud.id if last_solicitud else 0
#             validated_data['numeroFormulario'] = f"SF-{last_number + 1:04d}"
        
#         return super().create(validated_data)
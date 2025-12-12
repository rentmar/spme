# serializers.py 
from rest_framework import serializers
#from .models import SolicitudFondos, FormaPago, Usuario, Actividad, TareaActividad
from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from django.db import transaction


class SolicitudFondosCreateSerializer(serializers.ModelSerializer):
    # Campos que vendrán en el JSON con nombres diferentes a los del modelo
    forma_pago = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(),
        source='formaPago'
    )
    lugar_solicitud = serializers.CharField(source='lugarSolicitud')
    fecha_solicitud = serializers.DateField(source='fechaSolicitud')
    fecha_realizacion_actividad = serializers.DateField(
        source='fechaRealizacionActividad',
        required=False,
        allow_null=True
    )    
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
    contador_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='contador',
        required=False,
        allow_null=True
    )
    
    # Campo para bloquear iconos
    bloquear_icono_sf = serializers.BooleanField(
        source='bloquearIconosSolFondos',
        required=False,
        default=True
    )
    
    # Campo para número de formulario personalizado
    numero_formulario = serializers.CharField(
        source='numeroFormulario',
        required=False,
        allow_null=True,
        allow_blank=True
    )
    
    # Campo para actividad (JSON con datos de actualización)
    actividad = serializers.JSONField(write_only=True, required=False)
    
    id_tarea = serializers.PrimaryKeyRelatedField(
        queryset=TareaActividad.objects.all(),
        source='tarea',
        required=False,
        allow_null=True
    )

    # NUEVOS CAMPOS AGREGADOS - SIN source PORQUE COINCIDEN CON EL MODELO
    descripcion_actividad = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    
    objetivo_actividad = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    
    datos_forma_pago = serializers.JSONField(
        required=False,
        allow_null=True
    )

    # Campo id_actividad explícito para manejar la asignación directa
    id_actividad = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = SolicitudFondos
        fields = [
            'numero_formulario', 'detalle_destino_fondos', 'bloquear_icono_sf', 'forma_pago', 
            'lugar_solicitud', 'fecha_solicitud', 'fecha_realizacion_actividad', 'monto_solicitado', 
            'validacion_responsable', 'id_responsable', 'validacion_coordinador', 
            'id_coordinador', 'id_usuario', 'contador_id', 'actividad', 'id_tarea',
            # NUEVOS CAMPOS
            'descripcion_actividad', 'objetivo_actividad', 'datos_forma_pago',
            'id_actividad'
        ]

    @transaction.atomic
    def create(self, validated_data):
        # Extraer y procesar los datos de actividad si vienen
        actividad_data = validated_data.pop('actividad', None)
        id_actividad_directo = validated_data.pop('id_actividad', None)
        actividad_obj = None
        
        # Prioridad 1: Si viene actividad_data (objeto JSON), usar su id_actividad
        if actividad_data and 'id_actividad' in actividad_data:
            try:
                actividad_id = actividad_data['id_actividad']
                actividad_obj = Actividad.objects.select_for_update().get(id=actividad_id)
                
                # Actualizar los campos de la actividad si vienen en el JSON
                campos_actualizados = False
                if 'descripcion_actividad' in actividad_data:
                    actividad_obj.descripcion = actividad_data['descripcion_actividad']
                    campos_actualizados = True
                if 'objetivo_actividad' in actividad_data:
                    actividad_obj.objetivo_de_actividad = actividad_data['objetivo_actividad']
                    campos_actualizados = True
                
                if campos_actualizados:
                    actividad_obj.save()
                
            except Actividad.DoesNotExist:
                raise serializers.ValidationError(
                    {"actividad": f"La actividad con ID {actividad_id} no existe."}
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {"actividad": f"Error al actualizar la actividad: {str(e)}"}
                )
        
        # Prioridad 2: Si no se procesó arriba pero viene id_actividad directo
        elif id_actividad_directo:
            try:
                actividad_obj = Actividad.objects.get(id=id_actividad_directo)
            except Actividad.DoesNotExist:
                raise serializers.ValidationError(
                    {"id_actividad": f"La actividad con ID {id_actividad_directo} no existe."}
                )

        # Asignar el objeto actividad a validated_data si se encontró
        if actividad_obj:
            validated_data['actividad'] = actividad_obj
        
        # Procesar los nuevos campos directamente en la solicitud de fondos
        # Estos campos se guardarán directamente en el modelo SolicitudFondos
        if 'descripcion_actividad' in validated_data:
            # Este campo se guarda directamente en SolicitudFondos
            pass  # No necesita procesamiento especial
        
        if 'objetivo_actividad' in validated_data:
            # Este campo se guarda directamente en SolicitudFondos
            pass  # No necesita procesamiento especial
        
        if 'datos_forma_pago' in validated_data:
            # Validar que sea un JSON válido
            datos_forma_pago = validated_data['datos_forma_pago']
            if datos_forma_pago and not isinstance(datos_forma_pago, (dict, list)):
                raise serializers.ValidationError(
                    {"datos_forma_pago": "Los datos de forma de pago deben ser un objeto JSON válido."}
                )
        
        try:
            # Limpiar campos que no pertenecen al modelo pero están en validated_data por el serializer
            if 'responsable' in validated_data:
                # Si existe contador, preferimos ese. Si no, usamos responsable como contador si se desea, 
                # pero aqui solo lo eliminamos para evitar el error.
                # O si se quiere dar soporte a id_responsable como alias de contador:
                # if 'contador' not in validated_data:
                #    validated_data['contador'] = validated_data.pop('responsable')
                # else:
                validated_data.pop('responsable')

            # Crear la solicitud de fondos dentro de la misma transacción
            solicitud = super().create(validated_data)
            
            # Generar número de formulario basado en el ID real y Código de Actividad
            # Formato: {codigo_actividad} - SF {id}
            codigo_actividad = "SN"
            if solicitud.actividad and solicitud.actividad.codigo:
                codigo_actividad = solicitud.actividad.codigo
            
            # Siempre regenerar el número de formulario para asegurar el formato correcto
            solicitud.numeroFormulario = f"{codigo_actividad} - SF {solicitud.id:05d}"
            solicitud.save(update_fields=['numeroFormulario'])

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
#     fecha_realizacion_actividad = serializers.DateField(  # NUEVO CAMPO
#         source='fechaRealizacionActividad',
#         required=False,
#         allow_null=True
#     )    
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
    
#     # Campo para bloquear iconos
#     bloquear_icono_sf = serializers.BooleanField(
#         source='bloquearIconosSolFondos',
#         required=False,
#         default=True
#     )
    
#     # Campo para número de formulario personalizado
#     numero_formulario = serializers.CharField(
#         source='numeroFormulario',
#         required=False,
#         allow_null=True,
#         allow_blank=True
#     )
    
#     # Campo para actividad (JSON con datos de actualización)
#     actividad = serializers.JSONField(write_only=True, required=False)
    
#     id_tarea = serializers.PrimaryKeyRelatedField(
#         queryset=TareaActividad.objects.all(),
#         source='tarea',
#         required=False,
#         allow_null=True
#     )

#     class Meta:
#         model = SolicitudFondos
#         fields = [
#             'numero_formulario', 'detalle_destino_fondos', 'bloquear_icono_sf', 'forma_pago', 
#             'lugar_solicitud', 'fecha_solicitud', 'fecha_realizacion_actividad', 'monto_solicitado', 
#             'validacion_responsable', 'id_responsable', 'validacion_coordinador', 
#             'id_coordinador', 'id_usuario', 'actividad', 'id_tarea'
#         ]

#     @transaction.atomic
#     def create(self, validated_data):
#         # Extraer y procesar los datos de actividad si vienen
#         actividad_data = validated_data.pop('actividad', None)
#         actividad_obj = None
        
#         # Si viene actividad en el formato, actualizar la actividad existente
#         if actividad_data and 'id_actividad' in actividad_data:
#             try:
#                 actividad_id = actividad_data['id_actividad']
#                 actividad_obj = Actividad.objects.select_for_update().get(id=actividad_id)
                
#                 # Actualizar los campos de la actividad si vienen en el JSON
#                 campos_actualizados = False
#                 if 'descripcion_actividad' in actividad_data:
#                     actividad_obj.descripcion = actividad_data['descripcion_actividad']
#                     campos_actualizados = True
#                 if 'objetivo_actividad' in actividad_data:
#                     actividad_obj.objetivo_de_actividad = actividad_data['objetivo_actividad']
#                     campos_actualizados = True
                
#                 if campos_actualizados:
#                     actividad_obj.save()
                
#                 # Asignar la actividad actualizada a la solicitud de fondos
#                 validated_data['actividad'] = actividad_obj
                
#             except Actividad.DoesNotExist:
#                 raise serializers.ValidationError(
#                     {"actividad": f"La actividad con ID {actividad_id} no existe."}
#                 )
#             except Exception as e:
#                 raise serializers.ValidationError(
#                     {"actividad": f"Error al actualizar la actividad: {str(e)}"}
#                 )
        
#         # Generar número de formulario automáticamente solo si no se proporcionó uno
#         if ('numeroFormulario' not in validated_data or 
#             not validated_data.get('numeroFormulario')):
#             last_solicitud = SolicitudFondos.objects.order_by('-id').first()
#             last_number = last_solicitud.id if last_solicitud else 0
#             validated_data['numeroFormulario'] = f"SF-{last_number + 1:04d}"
        
#         try:
#             # Crear la solicitud de fondos dentro de la misma transacción
#             solicitud = super().create(validated_data)
#             return solicitud
            
#         except Exception as e:
#             # Si hay algún error al crear la solicitud, la transacción se revertirá
#             # automáticamente incluyendo cualquier cambio en la actividad
#             raise serializers.ValidationError(
#                 {"solicitud": f"Error al crear la solicitud de fondos: {str(e)}"}
#             )

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
    
#     # Cambiar el campo id_actividad para manejar el nuevo formato
#     actividad = serializers.JSONField(write_only=True, required=False)
    
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
#             'id_usuario', 'actividad', 'id_tarea, numero_formulario'
#         ]

#     @transaction.atomic
#     def create(self, validated_data):
#         # Extraer y procesar los datos de actividad si vienen en el nuevo formato
#         actividad_data = validated_data.pop('actividad', None)
#         actividad_obj = None
        
#         # Si viene actividad en el nuevo formato, actualizar la actividad existente
#         if actividad_data and 'id_actividad' in actividad_data:
#             try:
#                 actividad_id = actividad_data['id_actividad']
#                 actividad_obj = Actividad.objects.select_for_update().get(id=actividad_id)
                
#                 # Actualizar los campos de descripción y objetivo si vienen en el JSON
#                 campos_actualizados = False
#                 if 'descripcion_actividad' in actividad_data:
#                     actividad_obj.descripcion = actividad_data['descripcion_actividad']
#                     campos_actualizados = True
#                 if 'objetivo_actividad' in actividad_data:
#                     actividad_obj.objetivo_de_actividad = actividad_data['objetivo_actividad']
#                     campos_actualizados = True
                
#                 if campos_actualizados:
#                     actividad_obj.save()
                
#                 # Asignar la actividad actualizada a la solicitud de fondos
#                 validated_data['actividad'] = actividad_obj
                
#             except Actividad.DoesNotExist:
#                 raise serializers.ValidationError(
#                     {"actividad": f"La actividad con ID {actividad_id} no existe."}
#                 )
#             except Exception as e:
#                 raise serializers.ValidationError(
#                     {"actividad": f"Error al actualizar la actividad: {str(e)}"}
#                 )
        
#         # Generar número de formulario automáticamente si no viene
#         if 'numeroFormulario' not in validated_data or not validated_data.get('numeroFormulario'):
#             last_solicitud = SolicitudFondos.objects.order_by('-id').first()
#             last_number = last_solicitud.id if last_solicitud else 0
#             validated_data['numeroFormulario'] = f"SF-{last_number + 1:04d}"
        
#         try:
#             # Crear la solicitud de fondos dentro de la misma transacción
#             solicitud = super().create(validated_data)
#             return solicitud
            
#         except Exception as e:
#             # Si hay algún error al crear la solicitud, la transacción se revertirá
#             # automáticamente incluyendo cualquier cambio en la actividad
#             raise serializers.ValidationError(
#                 {"solicitud": f"Error al crear la solicitud de fondos: {str(e)}"}
#             )



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
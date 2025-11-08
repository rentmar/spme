from ..models import SolicitudViaje
import datetime
import uuid

class SolicitudViajeDataAccess:

    def generar_numero_formulario(self):
        """Genera automáticamente el número de formulario"""
        try:
            today = datetime.date.today()
            year = today.year
            month = today.month
            
            # Contar cuántas solicitudes de viaje hay este mes
            count = SolicitudViaje.objects.filter(
                fechaSolicitud__year=year,
                fechaSolicitud__month=month
            ).count()
            
            next_number = count + 1
            return f"SV-{year}{month:02d}-{next_number:03d}"
        except Exception as e:
            # Si hay error, generar número basado en timestamp
            return f"SV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def crearSolicitudViaje(self, solicitudData):
        """
        Crea una nueva solicitud de viaje en la base de datos.
        
        :param solicitud_data: Datos de la solicitud de viaje.
        :return: Resultado de la creación de la solicitud.
        """
        # Generar número de formulario único con UUID
        today = datetime.date.today()
        unique_id = str(uuid.uuid4())[:8].upper()  # Primeros 8 caracteres del UUID
        
        numero_formulario = f"SV-{today.year}{today.month:02d}-{unique_id}"
        
        # Agregar número de formulario a los datos
        solicitudData['numeroFormulario'] = numero_formulario
        
        # Asegurar que datosSV esté presente
        # if 'datosSV' not in solicitudData:
        #     solicitudData['datosSV'] = {}
        
        # Crear la solicitud
        solicitud = SolicitudViaje.objects.create(**solicitudData)
        
        return solicitud
    
    def _generar_numero_formulario_unico(self):
        """
        Genera un número de formulario único basado en el conteo del mes
        """
        today = datetime.date.today()
        year = today.year
        month = today.month
        
        # Contar solicitudes del mes actual (incluye la transacción actual)
        count = SolicitudViaje.objects.filter(
            fechaSolicitud__year=year,
            fechaSolicitud__month=month
        ).count()
        
        # El nuevo número será count + 1
        nuevo_numero = count + 1
        
        return f"SV-{year}{month:02d}-{nuevo_numero:03d}"

    def obtenerSolicitudesViaje(self, filtros):
        """
        Obtiene solicitudes de viaje aplicando filtros
        """
        queryset = SolicitudViaje.objects.all()

        # Aplicar filtros si están presentes
        if filtros.get('id_solicitud_viaje'):
            queryset = queryset.filter(id=filtros['id_solicitud_viaje'])
        if filtros.get('id_actividad'):
            queryset = queryset.filter(actividad_id=filtros['id_actividad'])
        if filtros.get('id_tarea'):
            queryset = queryset.filter(tarea_id=filtros['id_tarea'])
        if filtros.get('usuario'):
            queryset = queryset.filter(usuario_id=filtros['usuario'])

        return queryset
    
    def actualizarValidacionSolicitudViaje(self, solicitudData):
        solicitud_id = solicitudData.get('solicitud_viaje_id')
        
        try:
            solicitud = SolicitudViaje.objects.get(id=solicitud_id)
            campos_actualizados = False

            if solicitudData.get('validacion_responsable') is not None:
                solicitud.validacionResponsable = solicitudData['validacion_responsable']
                campos_actualizados = True

            if solicitudData.get('validacion_coordinador') is not None:
                solicitud.validacionCoordinador = solicitudData['validacion_coordinador']
                campos_actualizados = True

            if campos_actualizados:
                solicitud.save()
                return {
                    "id": solicitud.id,
                    "mensaje": "Validaciones actualizadas exitosamente",
                    "validacion_responsable": solicitud.validacionResponsable,
                    "validacion_coordinador": solicitud.validacionCoordinador
                }
            else:
                return {"mensaje": "No se proporcionaron campos de validación para actualizar"}
                
        except SolicitudViaje.DoesNotExist:
            return {"mensaje": f"La solicitud de viaje con ID {solicitud_id} no existe"}
        except Exception as e:
            return {"mensaje": f"Error al actualizar las validaciones: {str(e)}"}
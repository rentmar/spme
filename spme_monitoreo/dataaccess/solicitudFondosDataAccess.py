from ..models import SolicitudFondos
from django.db.models import Q
from spme_actividades.models import Actividad

class SolicitudFondosDataAccess:
    
    def crearSolicitudFondos(self, solicitudData):
        """
        Crea una nueva solicitud de fondos en la base de datos.

        :param solicitud_data: Datos de la solicitud de fondos.
        :return: Resultado de la creación de la solicitud.
        """
        print("Datos recibidos en DataAccess:", solicitudData)  # DEBUG
        try:
            # Mapeo explícito de campos para asegurar que coincidan con el modelo
            mapped_data = {
                'detalleDestinoFondos': solicitudData.get('detalleDestinoFondos'),
                'formaPago_id': solicitudData.get('formaPago_id'),
                'lugarSolicitud': solicitudData.get('lugarSolicitud'),
                'fechaSolicitud': solicitudData.get('fechaSolicitud'),
                'fechaRealizacionActividad': solicitudData.get('fechaRealizacionActividad'),
                'montoSolicitado': solicitudData.get('montoSolicitado'),
                'validacionResponsable': solicitudData.get('validacionResponsable'),
                'contador_id': solicitudData.get('contador_id'),
                'validacionCoordinador': solicitudData.get('validacionCoordinador'),
                'coordinador_id': solicitudData.get('coordinador_id'),
                'usuario_id': solicitudData.get('usuario_id'),
                'actividad_id': solicitudData.get('actividad_id'),
                'tarea_id': solicitudData.get('tarea_id'),
                'numeroFormulario': "TEMP", # Se actualizará después
                'descripcion_actividad': solicitudData.get('descripcion_actividad'),
                'objetivo_actividad': solicitudData.get('objetivo_actividad'),
                'datos_forma_pago': solicitudData.get('datos_forma_pago'),
                'bloquearIconosSolFondos': solicitudData.get('bloquearIconosSolFondos'),
            }
            
            # NO filtrar campos opcionales - permitir que se guarden como None si es necesario
            # mapped_data = {k: v for k, v in mapped_data.items() if v is not None}  # COMENTADO
            
            print("Datos mapeados en DataAccess con TEMP numeroFormulario:", mapped_data)
            solicitud = SolicitudFondos.objects.create(**mapped_data)
            print("Solicitud creada con ID:", solicitud.id)
            
            # Generar numeroFormulario: {codigo_actividad} - SF {id}
            # Ejemplo: ACT - SF 00012
            actividad_id = solicitudData.get('actividad_id')
            codigo_actividad = "SN"
            
            if actividad_id:
                try:
                   actividad = Actividad.objects.get(id=actividad_id)
                   codigo_actividad = actividad.codigo if actividad.codigo else "SN"
                except Actividad.DoesNotExist:
                   codigo_actividad = "SN"
            
            nuevo_numero_formulario = f"{codigo_actividad} - SF {solicitud.id:05d}"
            solicitud.numeroFormulario = nuevo_numero_formulario
            solicitud.save()
            print(f"numeroFormulario actualizado a: {solicitud.numeroFormulario}")

            # Verificar los campos guardados
            solicitud_refreshed = SolicitudFondos.objects.get(id=solicitud.id)
            print("Campos guardados:")
            print("numeroFormulario:", solicitud_refreshed.numeroFormulario)
            print("descripcion_actividad:", solicitud_refreshed.descripcion_actividad)
            print("objetivo_actividad:", solicitud_refreshed.objetivo_actividad)
            print("datos_forma_pago:", solicitud_refreshed.datos_forma_pago)
            print("fechaRealizacionActividad:", solicitud_refreshed.fechaRealizacionActividad)
            print("bloquearIconosSolFondos:", solicitud_refreshed.bloquearIconosSolFondos)
            return solicitud_refreshed
        except Exception as e:
            print("❌ Error en DataAccess:", str(e))
            print("Tipo de error:", type(e).__name__)
            import traceback
            print("Traceback:", traceback.format_exc())
            raise e

    def obtenerSolicitudesFondos(self):
        """
        Obtiene todas las solicitudes de fondos de la base de datos.

        :return: Lista de solicitudes de fondos.
        """
        return SolicitudFondos.objects.all()
    
    def obtenerSolicitudesPorFiltros(self, actividad_id, usuario_id, tarea_id=None):
        """
        Obtiene solicitudes de fondos filtrando por actividad_id, usuario_id y tarea_id.
        Si tarea_id es null, solo filtra por actividad_id y usuario_id.
        
        :param actividad_id: ID de la actividad
        :param usuario_id: ID del usuario
        :param tarea_id: ID de la tarea (opcional)
        :return: Lista de solicitudes de fondos que coinciden con los filtros
        """
        # Construir el filtro base
        filtro = Q(actividad_id=actividad_id) & Q(usuario_id=usuario_id)
        
        # Si tarea_id está especificado, agregarlo al filtro
        if tarea_id:
            filtro &= Q(tarea_id=tarea_id)
        else:
            # Si tarea_id es null, buscar donde tarea_id es null
            filtro &= Q(tarea_id__isnull=True)
        
        return SolicitudFondos.objects.filter(filtro)
    
    def actualizarValidacionSolicitudFondos(self, solicitudData):
        """
        Actualiza las validaciones de una solicitud de fondos existente.
        :param solicitud_data: Datos con las validaciones a actualizar.
        :return: Solicitud de fondos actualizada.
        """
        solicitud_id = solicitudData.get('solicitud_id')
        
        try:
            solicitud = SolicitudFondos.objects.get(id=solicitud_id)
            
            campos_actualizados = False
            
            # Verificar si el valor para 'validacion_responsable' existe y no es None
            if solicitudData.get('validacion_responsable') is not None:
                solicitud.validacionResponsable = solicitudData['validacion_responsable']
                campos_actualizados = True
                
            # Verificar si el valor para 'validacion_coordinador' existe y no es None
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
            
        except SolicitudFondos.DoesNotExist:
            return {
                "mensaje": f"La solicitud de fondos con ID {solicitud_id} no existe"
            }
        except Exception as e:
            return {
                "mensaje": f"Error al actualizar las validaciones: {str(e)}"
            }

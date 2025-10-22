from ..models import SolicitudFondos
from django.db.models import Q

class SolicitudFondosDataAccess:
    
    def crearSolicitudFondos(self, solicitudData):
        """
        Crea una nueva solicitud de fondos en la base de datos.

        :param solicitud_data: Datos de la solicitud de fondos.
        :return: Resultado de la creación de la solicitud.
        """
        return SolicitudFondos.objects.create(**solicitudData)

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

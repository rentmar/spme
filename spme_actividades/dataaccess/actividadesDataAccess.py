from ..models import Actividad

class ActividadesDataAccess:
    def __init__(self):
        pass

    def obtenerActividadesPorUsuario(self, usuarioId):
        """
        Obtiene las actividades asociadas a un usuario específico.

        :param usuarioId: ID del usuario cuyas actividades se desean obtener.
        :return: Lista de actividades del usuario.
        """
        #return Actividad.objects.filter(usuario_id=usuarioId)
        return Actividad.objects.all()
    
    def crearActividad(self,actividadRequest):
        return Actividad.objects.create(**actividadRequest)
    
    def obtenerActividadesGanttId(self,idResponsable):
        """
        Obtiene las actividades asociadas al diagrama de Gantt.
        :return: Lista de actividades del diagrama de Gantt.
        """
        return Actividad.objects.filter(
            responsable_id=idResponsable
        ).values(
            'codigo',
            'nombreCorto',
            'descripcion',
            'tipo_id',
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'gradoEjecucion',
            'estado'
        )

    def obtenerActividadPorId(self, actividadId):
        """
        Obtiene la actividad asociada a un ID específico.

        :param actividadId: ID de la actividad que se desea obtener.
        :return: Actividad correspondiente al ID proporcionado.
        """
        return Actividad.objects.filter(id=actividadId).first()
    
    def obtenerDatosFormActividadPorId(self, actividadId):
        """
        Obtiene los datos del formulario de actividad asociados a un ID específico.

        :param actividadId: ID de la actividad cuyos datos del formulario se desean obtener.
        :return: Datos del formulario correspondientes al ID proporcionado.
        """
        return Actividad.objects.filter(id=actividadId).values(
            'procedencia_fondos',
        ).first()

    def obtenerEncabezadoActividadPorId(self, encabezadoId):
        """
        Obtiene el encabezado de actividad asociado a un ID específico.

        :param encabezadoId: ID del encabezado de actividad que se desea obtener.
        :return: Encabezado de actividad correspondiente al ID proporcionado.
        """
        return Actividad.objects.filter(id=encabezadoId).values(
            "codigo",
            "descripcion",
            "estado",
            "fecha_programada",
            "fecha_cierre",
            "responsable_id",
            "presupuesto",
            "tipo_id"
        ).first()
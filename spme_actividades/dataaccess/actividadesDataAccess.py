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
    
    def obtenerActividadesPorKant(self):
        """
        Obtiene las actividades asociadas al diagrama de Kant.
        :return: Lista de actividades del diagrama de Kant.
        """
        return Actividad.objects.all().values(
        'codigo',
        'descripcion',
        'tipo_id',
        'fecha_programada',
        'duracion',
        'fecha_inicio',
        'fecha_cierre',
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
            'id',
            'descripcion',
            'fecha_inicio',
            'fecha_cierre',
            'objetivo_de_actividad',
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
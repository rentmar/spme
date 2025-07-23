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
    
    def obtenerActividadesPorKant(self):
        """
        Obtiene las actividades asociadas al diagrama de Kant.
        :return: Lista de actividades del diagrama de Kant.
        """
        return Actividad.objects.all().values(
        'codigo',
        'descripcion',
        'tipo',
        'fecha_programada',
        'duracion',
        'fecha_inicio',
        'fecha_cierre',
        'estado'
    )
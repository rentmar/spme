from ..models import Actividad
from django.db.models import Sum

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
    
    def obtenerActividadesGanttId(self):
        """
        Obtiene las actividades asociadas al diagrama de Gantt.
        :return: Lista de actividades del diagrama de Gantt.
        """
        return Actividad.objects.values(
            'codigo',
            'nombreCorto',
            'descripcion',
            'tipo_id',
            'fecha_programada',
            'fecha_inicio',
            'fecha_cierre',
            'gradoEjecucion',
            'estado',
            'responsable_id',
        )

    def obtenerActividadPorId(self, actividadId):
        """
        Obtiene la actividad asociada a un ID específico.

        :param actividadId: ID de la actividad que se desea obtener.
        :return: Actividad correspondiente al ID proporcionado.
        """
        return Actividad.objects.filter(id=actividadId)
    
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
        actividad = Actividad.objects.get(id=encabezadoId)

        data = {
                "codigo": actividad.codigo,
                "descripcion": actividad.descripcion,
                "estado": actividad.get_estado_display(), 
                "fecha_programada": actividad.fecha_programada,
                "fecha_cierre": actividad.fecha_cierre,
                "responsable_id": actividad.responsable_id,
                "presupuesto": actividad.presupuesto,
                "tipo_id": actividad.tipo_id
            }
        return data
            
    def totalActividadesPlanificadas(self):
        """
        Obtiene el total de actividades planificadas.

        :return: Total de actividades planificadas.
        """
        return Actividad.objects.filter(estado='PLAN').count()
    
    def totalActividadesEnEjecucion(self):
        """
        Obtiene el total de actividades en ejecución.

        :return: Total de actividades en ejecución.
        """
        return Actividad.objects.filter(estado='EJEC').count()
    
    def totalActividadesFinalizadas(self):
        """
        Obtiene el total de actividades finalizadas.

        :return: Total de actividades finalizadas.
        """
        return Actividad.objects.filter(estado='FIN').count()
    
    def sumaPresupuestosGlobales(self):
        """
        Obtiene la suma de los presupuestos globales de todas las actividades.

        :return: Suma de los presupuestos globales.
        """
        resultado = Actividad.objects.filter(estado='PLAN').aggregate(total_presupuestos_globales=Sum('presupuestoGlobal'))
        return resultado['total_presupuestos_globales'] if resultado['total_presupuestos_globales'] is not None else 0
    
    def sumaPresupuestos(self):
        """
        Obtiene la suma de los presupuestos de todas las actividades.

        :return: Suma de los presupuestos.
        """
        resultado = Actividad.objects.filter(estado='PLAN').aggregate(total_presupuestos=Sum('presupuesto'))
        return resultado['total_presupuestos'] if resultado['total_presupuestos'] is not None else 0
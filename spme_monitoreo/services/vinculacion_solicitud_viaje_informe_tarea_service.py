#spme/spme_monitoreo/services/vinculacion_solicitud_viaje_informe_tarea_service.py
import logging
from spme_monitoreo.models import VinculacionSolicitudInformeTarea, SolicitudViaje
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)


class VinculacionSolicitudViajeInformeTareaService:
    """
    Servicio para gestionar vinculaciones de
    Solicitudes de Viaje a Informes de Tarea/SubActividad
    """

    @staticmethod
    def crear_lote_desde_json(informe, vinculacion_json, usuario_id=None):
        """
        Crea las vinculaciones desde el JSON vinculacionSolViajes
        
        ARGS:
            informe: Instancia de InformeTareaPrincipal
            vinculacion_json: Bloque de vinculacionSolViajes del JSON
            usuario_id(int): ID del usuario que realiza la vinculacion
        
        Returns:
            list: vinculaciones creadas            
        """
        creadas = []
        #Solicitudes para ser vinculadas al informe de tarea/subactividad
        solicitudes = vinculacion_json.get('solicitudes_vinculadas', [])
        usuario = None

        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"Usuario {usuario_id} no encontrado")
        
        #Crear las vinculaciones
        for sol_json in solicitudes:
            vinculacion = VinculacionSolicitudViajeInformeTareaService._crear_individual(
                informe, sol_json, usuario
            )
            if vinculacion:
                creadas.append(vinculacion)
        logger.info(f"Vinculaciones creadas: {len(creadas)} de {len(solicitudes)}")
        return creadas
        
    @staticmethod
    def _crear_individual(informe, sol_json, usuario):
        """
        Crea una vinculacion individual para las solicitudes de viaje tarea
        """
        id_solicitud = sol_json.get('id_solicitud_viaje')
        solicitud = None

        if(id_solicitud):
            try:
                solicitud = SolicitudViaje.objects.get(id=int(id_solicitud))
            except SolicitudViaje.DoesNotExist:
                logger.warning(f"SolicitudViaje {id_solicitud} no encontrada")
                return None
        
        if not solicitud:
            return None
        
        #Comprobar si existe ua vinculacion previa
        existe = VinculacionSolicitudInformeTarea.objects.filter(
            solicitud = solicitud,
            informe = informe,
        ).exists()

        #Retorno si existe un vinculo previo
        if existe:
            logger.info(f"Vinculación ya existe para solicitud {id_solicitud} - ignorando")
            return None
        
        #Crea la vinculacion
        vinculacion = VinculacionSolicitudInformeTarea(
            solicitud = solicitud,
            informe = informe,
            usuario_vinculo = usuario,
            activa = True,
            datos_completos_vinculacion = sol_json
        )
        vinculacion.save()
        logger.info(f"Vinculación creada - Solicitud: {id_solicitud} → Informe: {informe.numeroInforme}")
        return vinculacion
    
    @staticmethod
    def obtener_por_informe(informe_id):
        return VinculacionSolicitudInformeTarea.objects.filter(
            informe_id = informe_id,
            activa = True,
        ).select_related('solicitud')
    
    @staticmethod
    def desactivar_por_informe(informe_id):
        VinculacionSolicitudInformeTarea.objects.filter(
            informe_id=informe_id, 
            activa=True,
        ).update(activa=False)
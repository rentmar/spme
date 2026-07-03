import logging
from spme_validaciones.models import ValidacionSolicitudReembolso
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)

class ValidacionSolicitudReembolsoService:
    """
    Servicio para validaciones de Solicitudes de Reembolso.
    """
    @staticmethod
    def crear_desde_json(solicitud, validador_json):
        """Crea una validación desde datos JSON del validador."""
        usuario_id = validador_json.get('id')
        usuario = None
        
        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"⚠️ Usuario validador con ID {usuario_id} no encontrado")
                return None
        
        if not usuario:
            return None
        
        existe = ValidacionSolicitudReembolso.objects.filter(
            solicitud=solicitud, usuarioValidador=usuario
        ).exists()
        
        if existe:
            logger.info(f"ℹ️ Validación ya existe para {usuario.username} - ignorando")
            return None
        
        validacion = ValidacionSolicitudReembolso(
            solicitud=solicitud,
            usuarioValidador=usuario,
            usuarioRedactor=solicitud.usuario,
            estado=validador_json.get('estado', 'PENDIENTE'),
            versionDocumento='1',
        )
        validacion.save()
        logger.info(f"✅ Validación creada - {validacion.codigoSeguimiento}")
        return validacion
    
    @staticmethod
    def crear_lote_desde_json(solicitud, validadores_json):
        """Crea múltiples validaciones desde una lista JSON."""
        creadas = []
        omitidas = 0
        
        for validador in validadores_json:
            validacion = ValidacionSolicitudReembolsoService.crear_desde_json(
                solicitud, validador
            )
            if validacion:
                creadas.append(validacion)
            else:
                omitidas += 1
        
        logger.info(f"✅ Lote procesado: {len(creadas)} creadas, {omitidas} omitidas")
        return creadas
    
    @staticmethod
    def actualizar_estado(validacion_id, nuevo_estado, comentarios=None):
        from spme_validaciones.repositories.validacion_solicitud_reembolso_repository import (
            ValidacionSolicitudReembolsoRepository
        )
        repo = ValidacionSolicitudReembolsoRepository()
        return repo.actualizar_estado(validacion_id, nuevo_estado, comentarios)
    
    @staticmethod
    def obtener_resumen_estado(solicitud_id):
        from spme_validaciones.repositories.validacion_solicitud_reembolso_repository import (
            ValidacionSolicitudReembolsoRepository
        )
        repo = ValidacionSolicitudReembolsoRepository()
        return repo.obtener_resumen_estado_solicitud(solicitud_id)

    @staticmethod
    def obtener_estadisticas(solicitud_id):
        from spme_validaciones.repositories.validacion_solicitud_reembolso_repository import (
            ValidacionSolicitudReembolsoRepository
        )
        repo = ValidacionSolicitudReembolsoRepository()
        return repo.obtener_estadisticas_por_solicitud(solicitud_id)
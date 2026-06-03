import logging
from spme_validaciones.models import ValidacionInformeTarea
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)


class ValidacionInformeTareaService:
    """
    Servicio para gestionar validaciones de Informes de Tarea (Subactividad).
    
    Maneja:
    - Crear validaciones individuales o en lote desde JSON
    - Actualizar estado (PENDIENTE → APROBADO/RECHAZADO)
    - Consultar por informe, validador o estado
    - Eliminar validaciones
    """

    # ============================================================
    # CREAR
    # ============================================================
    
    @staticmethod
    def crear_desde_json(informe_tarea, validador_json):
        """
        Crea una validación a partir de un JSON de validador.
        
        Args:
            informe_tarea: Instancia de InformeTareaPrincipal
            validador_json (dict): {
                "id": 68,
                "nombre_completo": "Mark Rolqueza Bernal",
                "email": "rolquezamarcelo@gmail.com",
                "rol": "coordinador",
                "username": "mkrolqueza",
                "estado": "PENDIENTE",
                "estado_display": "Pendiente",
                "fechaAsignacion": "2026-05-28T03:30:51.091Z"
            }
        
        Returns:
            ValidacionInformeTarea o None si el usuario no existe o ya está asignado
        """
        usuario_id = validador_json.get('id')
        usuario = None
        
        # Obtener usuario
        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"⚠️  Usuario validador con ID {usuario_id} no encontrado")
                return None
        
        if not usuario:
            logger.warning(f"⚠️  No se pudo obtener usuario del JSON: {validador_json}")
            return None
        
        # Verificar si ya existe una validación para este usuario en este informe
        existe = ValidacionInformeTarea.objects.filter(
            informeTarea=informe_tarea,
            usuarioValidador=usuario
        ).exists()
        
        if existe:
            logger.info(f"ℹ️  Validación ya existe para {usuario.username} - ignorando")
            return None
        
        # Crear validación
        validacion = ValidacionInformeTarea(
            informeTarea=informe_tarea,
            usuarioValidador=usuario,
            usuarioRedactor=informe_tarea.usuario,
            estado=validador_json.get('estado', 'PENDIENTE'),
            versionDocumento='1',
        )
        validacion.save()
        
        logger.info(f"✅ Validación creada - {validacion.codigoSeguimiento} "
                   f"| Validador: {usuario.username} "
                   f"| Rol: {validador_json.get('rol', 'N/A')} "
                   f"| Estado: {validacion.estado}")
        
        return validacion

    @staticmethod
    def crear_lote_desde_json(informe_tarea, validadores_json):
        """
        Crea múltiples validaciones desde una lista de JSON.
        
        Args:
            informe_tarea: Instancia de InformeTareaPrincipal
            validadores_json (list): Lista de dicts con datos de validadores
        
        Returns:
            list: Validaciones creadas exitosamente
        """
        if not validadores_json:
            logger.info("ℹ️  Lista de validadores vacía")
            return []
        
        creadas = []
        omitidas = 0
        
        for validador in validadores_json:
            validacion = ValidacionInformeTareaService.crear_desde_json(
                informe_tarea, validador
            )
            if validacion:
                creadas.append(validacion)
            else:
                omitidas += 1
        
        logger.info(f"✅ Lote procesado: {len(creadas)} creadas, "
                   f"{omitidas} omitidas de {len(validadores_json)}")
        
        return creadas

    # ============================================================
    # ACTUALIZAR
    # ============================================================
    
    @staticmethod
    def actualizar_estado(validacion_id, nuevo_estado, comentarios=None):
        """
        Actualiza el estado de una validación.
        
        Args:
            validacion_id (int): ID de la validación
            nuevo_estado (str): 'APROBADO' o 'RECHAZADO'
            comentarios (str, optional): Comentarios del validador
        
        Returns:
            ValidacionInformeTarea actualizada
        
        Raises:
            ValueError: Si la validación no existe
        """
        validacion = ValidacionInformeTareaService.obtener_por_id(validacion_id)
        
        if not validacion:
            raise ValueError(f"Validación con ID {validacion_id} no encontrada")
        
        estado_anterior = validacion.estado
        validacion.estado = nuevo_estado
        
        if comentarios:
            validacion.comentarios = comentarios
        
        validacion.save()
        
        logger.info(f"✅ Validación actualizada - {validacion.codigoSeguimiento}: "
                   f"{estado_anterior} → {nuevo_estado}")
        
        return validacion

    @staticmethod
    def actualizar_lote_estado(informe_tarea_id, nuevo_estado):
        """
        Actualiza el estado de todas las validaciones PENDIENTES de un informe.
        Útil para aprobar/rechazar en lote.
        """
        actualizadas = ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id,
            estado='PENDIENTE'
        ).update(estado=nuevo_estado)
        
        logger.info(f"✅ Lote actualizado: {actualizadas} → {nuevo_estado}")
        return actualizadas

    # ============================================================
    # OBTENER
    # ============================================================
    
    @staticmethod
    def obtener_por_id(validacion_id):
        """
        Obtiene una validación por su ID.
        
        Returns:
            ValidacionInformeTarea o None
        """
        try:
            return ValidacionInformeTarea.objects.select_related(
                'usuarioValidador', 'usuarioRedactor', 'informeTarea'
            ).get(id=validacion_id)
        except ValidacionInformeTarea.DoesNotExist:
            return None

    @staticmethod
    def obtener_por_informe(informe_tarea_id):
        """
        Obtiene todas las validaciones de un informe de tarea.
        
        Returns:
            QuerySet ordenado por fecha de asignación (más reciente primero)
        """
        return ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id
        ).select_related('usuarioValidador').order_by('-fechaAsignacion')

    @staticmethod
    def obtener_por_validador(usuario_id):
        """
        Obtiene todas las validaciones asignadas a un usuario.
        
        Returns:
            QuerySet ordenado por fecha de asignación (más reciente primero)
        """
        return ValidacionInformeTarea.objects.filter(
            usuarioValidador_id=usuario_id
        ).select_related('informeTarea').order_by('-fechaAsignacion')

    @staticmethod
    def obtener_pendientes_por_informe(informe_tarea_id):
        """
        Obtiene solo las validaciones PENDIENTES de un informe.
        """
        return ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id,
            estado='PENDIENTE'
        ).select_related('usuarioValidador')

    @staticmethod
    def obtener_aprobadas_por_informe(informe_tarea_id):
        """
        Obtiene solo las validaciones APROBADAS de un informe.
        """
        return ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id,
            estado='APROBADO'
        ).select_related('usuarioValidador')

    @staticmethod
    def obtener_rechazadas_por_informe(informe_tarea_id):
        """
        Obtiene solo las validaciones RECHAZADAS de un informe.
        """
        return ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id,
            estado='RECHAZADO'
        ).select_related('usuarioValidador')

    @staticmethod
    def obtener_resumen_estado(informe_tarea_id):
        """
        Obtiene un resumen de estados de validación para un informe.
        
        Returns:
            dict: {
                'total': 3,
                'pendientes': 1,
                'aprobados': 1,
                'rechazados': 1,
                'completado': False
            }
        """
        validaciones = ValidacionInformeTarea.objects.filter(informeTarea_id=informe_tarea_id)
        
        total = validaciones.count()
        pendientes = validaciones.filter(estado='PENDIENTE').count()
        aprobados = validaciones.filter(estado='APROBADO').count()
        rechazados = validaciones.filter(estado='RECHAZADO').count()
        
        return {
            'total': total,
            'pendientes': pendientes,
            'aprobados': aprobados,
            'rechazados': rechazados,
            'completado': pendientes == 0 and total > 0,
            'aprobado_totalmente': aprobados == total and total > 0,
        }

    # ============================================================
    # ELIMINAR
    # ============================================================
    
    @staticmethod
    def eliminar(validacion_id):
        """
        Elimina una validación por su ID.
        
        Returns:
            bool: True si se eliminó correctamente
        
        Raises:
            ValueError: Si la validación no existe
        """
        validacion = ValidacionInformeTareaService.obtener_por_id(validacion_id)
        
        if not validacion:
            raise ValueError(f"Validación con ID {validacion_id} no encontrada")
        
        codigo = validacion.codigoSeguimiento
        validacion.delete()
        logger.info(f"🗑️  Validación eliminada - {codigo}")
        return True

    @staticmethod
    def eliminar_por_informe(informe_tarea_id):
        """
        Elimina todas las validaciones de un informe.
        Útil para reasignar validadores.
        
        Returns:
            int: Cantidad de validaciones eliminadas
        """
        count, _ = ValidacionInformeTarea.objects.filter(
            informeTarea_id=informe_tarea_id
        ).delete()
        
        logger.info(f"🗑️  {count} validaciones eliminadas del informe {informe_tarea_id}")
        return count
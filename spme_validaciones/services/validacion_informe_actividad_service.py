# spme_validaciones/services/validacion_informe_actividad_service.py

import logging
from spme_validaciones.models import ValidacionInformeActividad
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)


class ValidacionInformeActividadService:

    @staticmethod
    def crear_desde_json(informe, validador_json):
        usuario_id = validador_json.get('id')
        usuario = None
        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"Usuario validador con ID {usuario_id} no encontrado")
                return None

        if usuario:
            existe = ValidacionInformeActividad.objects.filter(
                informe=informe, usuarioValidador=usuario
            ).exists()
            if existe:
                logger.info(f"Validación ya existe para {usuario.username} - ignorando")
                return None

        validacion = ValidacionInformeActividad(
            informe=informe,
            usuarioValidador=usuario,
            usuarioRedactor=informe.usuario,
            estado=validador_json.get('estado', 'PENDIENTE'),
            versionDocumento='1',
        )
        validacion.save()
        logger.info(f"Validación creada - {validacion.codigoSeguimiento}")
        return validacion

    @staticmethod
    def crear_lote_desde_json(informe, validadores_json):
        creadas = []
        for validador in validadores_json:
            validacion = ValidacionInformeActividadService.crear_desde_json(informe, validador)
            if validacion:
                creadas.append(validacion)
        logger.info(f"Validaciones creadas: {len(creadas)} de {len(validadores_json)}")
        return creadas

    @staticmethod
    def actualizar_estado(validacion_id, nuevo_estado, comentarios=None):
        validacion = ValidacionInformeActividadService.obtener_por_id(validacion_id)
        if not validacion:
            raise ValueError(f"Validación con ID {validacion_id} no encontrada")
        validacion.estado = nuevo_estado
        if comentarios:
            validacion.comentarios = comentarios
        validacion.save()
        return validacion

    @staticmethod
    def obtener_por_id(validacion_id):
        try:
            return ValidacionInformeActividad.objects.get(id=validacion_id)
        except ValidacionInformeActividad.DoesNotExist:
            return None

    @staticmethod
    def obtener_por_informe(informe_id):
        return ValidacionInformeActividad.objects.filter(
            informe_id=informe_id
        ).select_related('usuarioValidador').order_by('-fechaAsignacion')

    @staticmethod
    def obtener_por_validador(usuario_id):
        return ValidacionInformeActividad.objects.filter(
            usuarioValidador_id=usuario_id
        ).select_related('informe').order_by('-fechaAsignacion')

    @staticmethod
    def obtener_pendientes_por_informe(informe_id):
        return ValidacionInformeActividad.objects.filter(
            informe_id=informe_id, estado='PENDIENTE'
        )

    @staticmethod
    def eliminar(validacion_id):
        validacion = ValidacionInformeActividadService.obtener_por_id(validacion_id)
        if not validacion:
            raise ValueError(f"Validación con ID {validacion_id} no encontrada")
        validacion.delete()
        return True
# spme/spme_validaciones/services/validacion_solicitud_fondos_service.py
import logging
from spme_validaciones.models import ValidacionSolicitudFondos, HistorialValidacion
from spme_autenticacion.models import Usuario
from spme_monitoreo.models import SolicitudFondos
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
#repositorio
from ..repositories.validacion_solicitud_fondos_repository import ValidacionSolicitudFondosRepository
#Notificacion
from spme_mensajes.services.notificacion_service import(
    crear_mensaje_revision_solicitud_fondos,
    enviar_notificacion_mensajeria_interna,
)
from spme_email.services.notificacion_service import NotificacionService

logger = logging.getLogger(__name__)

class ValidacionSolicitudFondosService:
    """
    Servicio para validaciones de Solicitudes de Fondos.
    """

    def __init__(self):
        self.repository = ValidacionSolicitudFondosRepository()
        self.notificacion_service = NotificacionService()
    


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
        
        existe = ValidacionSolicitudFondos.objects.filter(
            solicitud=solicitud, usuarioValidador=usuario
        ).exists()
        
        if existe:
            logger.info(f"ℹ️ Validación ya existe para {usuario.username} - ignorando")
            return None
        
        validacion = ValidacionSolicitudFondos(
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
            validacion = ValidacionSolicitudFondosService.crear_desde_json(
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
        """Actualiza el estado de una validación usando el repositorio."""
        from spme_validaciones.repositories.validacion_solicitud_fondos_repository import (
            ValidacionSolicitudFondosRepository
        )
        repo = ValidacionSolicitudFondosRepository()
        return repo.actualizar_estado(validacion_id, nuevo_estado, comentarios)
    
    @staticmethod
    def obtener_resumen_estado(solicitud_id):
        """Obtiene el resumen de estado de una solicitud."""
        from spme_validaciones.repositories.validacion_solicitud_fondos_repository import (
            ValidacionSolicitudFondosRepository
        )
        repo = ValidacionSolicitudFondosRepository()
        return repo.obtener_resumen_estado_solicitud(solicitud_id)

    @staticmethod
    def obtener_estadisticas(solicitud_id):
        """Obtiene estadísticas completas de una solicitud."""
        from spme_validaciones.repositories.validacion_solicitud_fondos_repository import (
            ValidacionSolicitudFondosRepository
        )
        repo = ValidacionSolicitudFondosRepository()
        return repo.obtener_estadisticas_por_solicitud(solicitud_id)

    # ===================================================================
    # MÉTODOS PARA GESTIÓN DE REVISORES
    # ===================================================================
    def listar_revisores(self, solicitud_id: int) -> dict:
        """
        Lista todos los revisores de una solicitud de fondos
        
        Args:
            solicitud_id: ID de la solicitud
        
        Returns:
            Dict con información de la solicitud y sus revisores
        
        Raises:
            ValueError: Si la solicitud no existe
        """
        # Verificar que la solicitud existe
        try:
            solicitud = SolicitudFondos.objects.select_related(
                'usuario', 'actividad', 'tarea'
            ).get(id=solicitud_id)
        except SolicitudFondos.DoesNotExist:
            raise ValueError(f'Solicitud de fondos {solicitud_id} no encontrada')

        #obtener revisores
        validaciones = self.repository.obtener_revisores_por_solicitud(solicitud_id)
        #Construir lista de revisores
        revisores = []
        for validacion in validaciones:
            validador = validacion.usuarioValidador
            revisores.append({
                'validacion_id': validacion.id,
                'codigo_seguimiento': validacion.codigoSeguimiento,
                'estado': validacion.estado,
                'estado_display': validacion.get_estado_display(),
                'fecha_asignacion': validacion.fechaAsignacion,
                'fecha_resolucion': validacion.fechaResolucion,
                'version_documento': validacion.versionDocumento,
                'comentarios': validacion.comentarios,
                'validador': {
                    'id': validador.id,
                    'username': validador.username,
                    'nombre_completo': validador.get_full_name() or validador.username,
                    'correo': validador.correo,
                    'cargo': validador.cargo,
                }
            })

        #Obtener resumen
        resumen = self.repository.obtener_resumen_estado_solicitud(solicitud_id)
        
        return {
            'solicitud': solicitud,
            'revisores': revisores,
            'resumen': resumen,
        }

    @transaction.atomic
    def actualizar_revisores(self, solicitud_id: int, cambios: list, usuario_editor, motivo: str = '') -> dict:
        """
        Actualiza los revisores de una solicitud (cambio total)
        
        Args:
            solicitud_id: ID de la solicitud
            cambios: Lista de dicts con {validacion_id, nuevo_validador_id}
            usuario_editor: Usuario que realiza el cambio
            motivo: Motivo del cambio (opcional)
        
        Returns:
            Dict con resultados de la operación
        
        Raises:
            ValueError: Si la solicitud no existe
            PermissionDenied: Si el usuario no es el redactor
            ValidationError: Si hay errores de validación
        """
        # Verificar que la solicitud existe
        try:
            solicitud = SolicitudFondos.objects.select_related('usuario').get(id=solicitud_id)
        except SolicitudFondos.DoesNotExist:
            raise ValueError(f'Solicitud de fondos {solicitud_id} no encontrada')
        
        # ✅ CORRECCIÓN: SOLO EL REDACTOR (ESTRICTO)
        # Sin excepciones para staff/superuser
        if solicitud.usuario_id != usuario_editor.id:
            raise PermissionDenied(
                f'Solo el redactor de la solicitud ({solicitud.usuario.get_full_name()}) '
                f'puede cambiar los revisores'
            )
        
        # Verificar que hay cambios
        if not cambios:
            raise ValidationError('Debe proporcionar al menos un cambio de revisor')
        
        # Verificar que los cambios son para TODAS las validaciones
        total_validaciones = self.repository.contar_revisores_por_solicitud(solicitud_id)
        if len(cambios) != total_validaciones:
            raise ValidationError(
                f'Debe proporcionar cambios para TODOS los revisores ({total_validaciones} requeridos)'
            )
        
        # Calcular nueva versión
        validaciones_actuales = self.repository.obtener_por_solicitud(solicitud_id)
        version_actual = validaciones_actuales.first().versionDocumento if validaciones_actuales.exists() else '1'
        try:
            nueva_version = str(int(version_actual) + 1)
        except ValueError:
            nueva_version = version_actual + '.1'
        
        # Procesar cambios
        resultados = []
        errores = []
        validadores_anteriores = []
        validadores_nuevos = []
        
        for cambio in cambios:
            validacion_id = cambio.get('validacion_id')
            nuevo_validador_id = cambio.get('nuevo_validador_id')
            
            try:
                if not validacion_id or not nuevo_validador_id:
                    raise ValueError('validacion_id y nuevo_validador_id son requeridos')
                
                # Obtener validación actual
                validacion = self.repository.obtener_revisor_por_id(validacion_id)
                if not validacion:
                    raise ValueError(f'Validación {validacion_id} no encontrada')
                
                # Verificar que pertenece a la solicitud
                if validacion.solicitud_id != solicitud_id:
                    raise ValueError(f'Validación {validacion_id} no pertenece a la solicitud {solicitud_id}')
                
                # Obtener nuevo validador
                try:
                    nuevo_validador = Usuario.objects.get(id=nuevo_validador_id)
                except Usuario.DoesNotExist:
                    raise ValueError(f'Usuario {nuevo_validador_id} no encontrado')
                
                # Verificar que no sea el mismo
                if validacion.usuarioValidador_id == nuevo_validador_id:
                    raise ValueError('El nuevo revisor es el mismo que el actual')
                
                # Verificar que no esté duplicado en otros cambios
                ids_nuevos = [c.get('nuevo_validador_id') for c in cambios]
                if ids_nuevos.count(nuevo_validador_id) > 1:
                    raise ValueError(f'El revisor {nuevo_validador_id} está duplicado en los cambios')
                
                # Verificar que el nuevo revisor no esté ya asignado a otra validación de la misma solicitud
                if self.repository.existe_validador(
                    solicitud_id, 'solicitud', nuevo_validador_id
                ):
                    raise ValueError(
                        f'El usuario {nuevo_validador.get_full_name()} ya está asignado como revisor de esta solicitud'
                    )
                
                # Guardar estado anterior para historial
                estado_anterior = validacion.estado
                
                # Actualizar revisor
                validacion_actualizada, validador_anterior = self.repository.actualizar_revisor(
                    validacion_id=validacion_id,
                    nuevo_validador=nuevo_validador,
                    nueva_version=nueva_version
                )
                
                # Registrar en historial
                comentario_historial = (
                    f"Cambio de revisor: {validador_anterior.get_full_name()} "
                    f"→ {nuevo_validador.get_full_name()}"
                )
                if motivo:
                    comentario_historial += f" - Motivo: {motivo}"
                
                HistorialValidacion.objects.create(
                    validacion=validacion_actualizada,
                    usuario=usuario_editor,
                    estado_anterior=estado_anterior,
                    estado_nuevo='PENDIENTE',
                    versionDocumento=nueva_version,
                    comentario=comentario_historial
                )
                
                resultados.append({
                    'validacion_id': validacion_id,
                    'validador_anterior': {
                        'id': validador_anterior.id,
                        'nombre': validador_anterior.get_full_name(),
                    },
                    'validador_nuevo': {
                        'id': nuevo_validador.id,
                        'nombre': nuevo_validador.get_full_name(),
                    },
                    'estado': 'ACTUALIZADO'
                })
                
                validadores_anteriores.append(validador_anterior)
                validadores_nuevos.append(nuevo_validador)
                
            except (ValueError, ValidationError) as e:
                errores.append({
                    'validacion_id': validacion_id,
                    'error': str(e)
                })
                raise
            except Exception as e:
                logger.error(f"Error actualizando revisor {validacion_id}: {e}", exc_info=True)
                errores.append({
                    'validacion_id': validacion_id,
                    'error': 'Error interno'
                })
                raise
        
        # Enviar notificaciones
        notificaciones = self._enviar_notificaciones_cambio_revisores(
            solicitud=solicitud,
            validadores_anteriores=validadores_anteriores,
            validadores_nuevos=validadores_nuevos,
            nueva_version=nueva_version,
            motivo=motivo,
            usuario_editor=usuario_editor
        )
        
        return {
            'solicitud': solicitud,
            'nueva_version': nueva_version,
            'resultados': resultados,
            'errores': errores,
            'total_actualizados': len(resultados),
            'notificaciones': notificaciones,
        }

 
    def _enviar_notificaciones_cambio_revisores(self, solicitud, validadores_anteriores, validadores_nuevos, nueva_version, motivo, usuario_editor):
        """
        Envía notificaciones según Opción C:
        - Mensajería interna para AMBOS (nuevos y anteriores)
        - Email SOLO para NUEVOS revisores
        """
        resultados = {
            'nuevos_revisores': {
                'mensajeria_interna': [],
                'emails': None
            },
            'anteriores_revisores': {
                'mensajeria_interna': []
            }
        }

        # ===================================================================
        # 1. MENSAJERÍA INTERNA PARA NUEVOS REVISORES
        # ===================================================================
        for validador in validadores_nuevos:
            try:
                crear_mensaje_revision_solicitud_fondos(
                    solicitud=solicitud,
                    validador={
                        'id': validador.id,
                        'nombre_completo': validador.get_full_name(),
                        'rol': validador.cargo or 'validador',
                        'estado': 'PENDIENTE',
                        'fechaAsignacion': str(timezone.now())
                    },
                    version=nueva_version
                )
                resultados['nuevos_revisores']['mensajeria_interna'].append({
                    'id': validador.id,
                    'nombre': validador.get_full_name(),
                    'notificado': True
                })
                logger.info(f"✅ Mensajería interna enviada a nuevo revisor: {validador.get_full_name()}")
            except Exception as e:
                logger.error(f"❌ Error notificando a nuevo revisor {validador.id}: {e}")
                resultados['nuevos_revisores']['mensajeria_interna'].append({
                    'id': validador.id,
                    'nombre': validador.get_full_name(),
                    'notificado': False,
                    'error': str(e)
                })

        # ===================================================================
        # 2. MENSAJERÍA INTERNA PARA ANTERIORES REVISORES
        # ===================================================================
        for validador in validadores_anteriores:
            try:
                # Usar la función genérica de mensajería interna
                enviar_notificacion_mensajeria_interna(
                    tipo='fondos',
                    accion='nueva_revision',  # Reutilizamos la acción existente
                    solicitud=solicitud,
                    destinatarios_ids=[validador.id],
                    base_url='',
                    version=nueva_version
                )
                resultados['anteriores_revisores']['mensajeria_interna'].append({
                    'id': validador.id,
                    'nombre': validador.get_full_name(),
                    'notificado': True
                })
                logger.info(f"✅ Mensajería interna enviada a revisor anterior: {validador.get_full_name()}")
            except Exception as e:
                logger.error(f"❌ Error notificando a revisor anterior {validador.id}: {e}")
                resultados['anteriores_revisores']['mensajeria_interna'].append({
                    'id': validador.id,
                    'nombre': validador.get_full_name(),
                    'notificado': False,
                    'error': str(e)
                })

        # ===================================================================
        # 3. EMAIL SOLO PARA NUEVOS REVISORES
        # ===================================================================
        if validadores_nuevos:
            try:
                ids_nuevos = [v.id for v in validadores_nuevos]
                email_result = self.notificacion_service.enviar(
                    tipo='fondos',
                    solicitud_id=solicitud.id,
                    accion='nueva_revision',
                    destinatarios_ids=ids_nuevos,
                    base_url=''
                )
                resultados['nuevos_revisores']['emails'] = email_result
                logger.info(f"✅ Emails enviados a nuevos revisores: {email_result}")
            except Exception as e:
                logger.error(f"❌ Error enviando emails a nuevos revisores: {e}")
                resultados['nuevos_revisores']['emails'] = {
                    'error': str(e)
                }
        
        return resultados
        
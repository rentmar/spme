#Repositorio para operaciones CRUD de los mensajes de usuarios
from django.db.models import Q, Count
from django.utils import timezone
from ..models import MensajeUsuario, EstadoMensaje, TipoMensaje
import logging

logger = logging.getLogger(__name__)

class MensajeRepository:
    """
    Repositorio para operaciones CRUD de mensajes
    """
    def obtener_mensajes_usuario(destinatario_id, estado=None, tipo=None, limit=50, offset=0):
        """
        Obtiene mensajes de un usuario con filtros opcionales
        
        Args:
            destinatario_id: ID del usuario destinatario
            estado: Filtro por estado ('no_leido', 'leido', etc.)
            tipo: Filtro por tipo ('privado', 'sistema', etc.)
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            QuerySet de mensajes
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                destinatario_id=destinatario_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO, EstadoMensaje.ELIMINADO]
            )
            #Aplicar filtros
            if estado:
                queryset = queryset.filter(estado=estado)

            if tipo:
                queryset = queryset.filter(tipo=tipo)

            #Excluir mensajes expirados
            queryset = queryset.filter(
                Q(fecha_expiracion__isnull=True) | 
                Q(fecha_expiracion__gt=timezone.now())
            )   

            return queryset.order_by('-prioridad', '-fecha_envio')[offset:offset + limit]
        except Exception as e:
            logger.error(f"Error obteniendo mensajes para usuario {destinatario_id}: {str(e)}")
            raise

    @staticmethod
    def contar_mensajes_usuario(destinatario_id, estado=None, tipo=None):    
        """
        Cuenta mensajes de un usuario con filtros
        
        Args:
            destinatario_id: ID del usuario
            estado: Filtro por estado
            tipo: Filtro por tipo
        
        Returns:
            Dict con conteos
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                destinatario_id=destinatario_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO, EstadoMensaje.ELIMINADO]
            )
            if estado:
                queryset = queryset.filter(estado=estado)
            
            if tipo:
                queryset = queryset.filter(tipo=tipo)
            
            # Conteo total
            total = queryset.count()
            
            # Conteo por estado
            conteo_estado = queryset.values('estado').annotate(
                count=Count('id')
            )
            
            # Conteo por tipo
            conteo_tipo = queryset.values('tipo').annotate(
                count=Count('id')
            )
            
            # Conteo no leídos
            no_leidos = queryset.filter(estado=EstadoMensaje.NO_LEIDO).count()
            
            return {
                'total': total,
                'no_leidos': no_leidos,
                'por_estado': {item['estado']: item['count'] for item in conteo_estado},
                'por_tipo': {item['tipo']: item['count'] for item in conteo_tipo}
            }
        
        except Exception as e:
            logger.error(f"Error contando mensajes para usuario {destinatario_id}: {str(e)}")
            raise

    @staticmethod
    def obtener_mensaje_por_id(mensaje_id, destinatario_id=None):
        """
        Obtiene un mensaje específico
        
        Args:
            mensaje_id: ID del mensaje
            destinatario_id: ID del usuario (para verificación de propiedad)
        
        Returns:
            MensajeUsuario o None
        """
        try:
            queryset = MensajeUsuario.objects.filter(pk=mensaje_id)
            if destinatario_id:
                queryset = queryset.filter(destinatario_id=destinatario_id)
            
            return queryset.first()
        
        except Exception as e:    
            logger.error(f"Error obteniendo mensaje {mensaje_id}: {str(e)}")
            raise

    @staticmethod
    def crear_mensaje(data):
        """
        Crea un nuevo mensaje
        
        Args:
            data: Diccionario con datos del mensaje
        
        Returns:
            MensajeUsuario creado
        """
        try:
            mensaje = MensajeUsuario(**data)
            mensaje.full_clean()
            mensaje.save()
            
            logger.info(f"Mensaje creado: {mensaje.pk} para usuario {mensaje.destinatario_id}")
            return mensaje
        
        except Exception as e:    
            logger.error(f"Error creando mensaje: {str(e)}")
            raise

    @staticmethod
    def actualizar_estado_mensaje(mensaje_id, nuevo_estado, destinatario_id=None):
        """
        Actualiza el estado de un mensaje
        
        Args:
            mensaje_id: ID del mensaje
            nuevo_estado: Nuevo estado
            destinatario_id: ID del usuario (para verificación)
        
        Returns:
            MensajeUsuario actualizado o None
        """
        try:
            mensaje = MensajeRepository.obtener_mensaje_por_id(mensaje_id, destinatario_id)
            
            if not mensaje:
                return None

            # Validar transición de estado
            transiciones_validas = {
                EstadoMensaje.NO_LEIDO: [EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO, EstadoMensaje.ELIMINADO],
                EstadoMensaje.LEIDO: [EstadoMensaje.NO_LEIDO, EstadoMensaje.ARCHIVADO, EstadoMensaje.ELIMINADO],
                EstadoMensaje.ARCHIVADO: [EstadoMensaje.LEIDO, EstadoMensaje.NO_LEIDO, EstadoMensaje.ELIMINADO],
                EstadoMensaje.ELIMINADO: []  # No se puede salir de eliminado
            }
            if nuevo_estado not in transiciones_validas.get(mensaje.estado, []):
                raise ValueError(f"Transición de estado inválida: {mensaje.estado} -> {nuevo_estado}")
            
            # Aplicar cambios según estado
            if nuevo_estado == EstadoMensaje.LEIDO and mensaje.estado == EstadoMensaje.NO_LEIDO:
                mensaje.marcar_como_leido(commit=False)
            elif nuevo_estado == EstadoMensaje.NO_LEIDO and mensaje.estado == EstadoMensaje.LEIDO:
                mensaje.marcar_como_no_leido(commit=False)
            elif nuevo_estado == EstadoMensaje.ARCHIVADO:
                mensaje.archivar(commit=False)
            elif nuevo_estado == EstadoMensaje.ELIMINADO:
                mensaje.eliminar(commit=False)
                
            mensaje.save()
            logger.info(f"Estado de mensaje {mensaje_id} actualizado: {mensaje.estado}")

            return mensaje

        except Exception as e:
            logger.error(f"Error actualizando estado de mensaje {mensaje_id}: {str(e)}")
            raise

    @staticmethod
    def marcar_varios_como_leido(mensaje_ids, destinatario_id):
        """
        Marca varios mensajes como leídos
        
        Args:
            mensaje_ids: Lista de IDs de mensajes
            destinatario_id: ID del usuario
        
        Returns:
            Número de mensajes actualizados
        """
        try:
            updated = MensajeUsuario.objects.filter(
                pk__in=mensaje_ids,
                destinatario_id=destinatario_id,
                estado=EstadoMensaje.NO_LEIDO
            ).update(
                estado=EstadoMensaje.LEIDO,
                fecha_leido=timezone.now()
            )
            
            logger.info(f"{updated} mensajes marcados como leídos para usuario {destinatario_id}")
            return updated

        except Exception as e:
            logger.error(f"Error marcando mensajes como leídos: {str(e)}")
            raise

    @staticmethod
    def buscar_mensajes(destinatario_id, query, limit=20):            
        """
        Busca mensajes por contenido
        
        Args:
            destinatario_id: ID del usuario
            query: Texto de búsqueda
            limit: Límite de resultados
        
        Returns:
            Lista de mensajes
        """
        try:
            return MensajeUsuario.objects.filter(
                destinatario_id=destinatario_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO],
            ).filter(
                Q(asunto__icontains=query) |
                Q(contenido__icontains=query) |
                Q(metadata__icontains=query)
            ).order_by('-fecha_envio')[:limit]
            
        except Exception as e:
            logger.error(f"Error buscando mensajes para usuario {destinatario_id}: {str(e)}")
            raise

    @staticmethod
    def limpiar_mensajes_expirados():
        """
        Limpia mensajes expirados (soft delete)
        
        Returns:
            Número de mensajes limpiados
        """
        try:
            expirados = MensajeUsuario.objects.filter(
                fecha_expiracion__isnull=False,
                fecha_expiracion__lte=timezone.now(),
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO]
            )
            
            count = expirados.count()
            expirados.update(estado=EstadoMensaje.ELIMINADO)
            
            logger.info(f"{count} mensajes expirados limpiados")
            return count
            
        except Exception as e:
            logger.error(f"Error limpiando mensajes expirados: {str(e)}")
            raise

    @staticmethod
    def obtener_mensajes_por_actividad(actividad_id, destinatario_id=None):
        """
        Obtiene mensajes relacionados con una actividad
        
        Args:
            actividad_id: ID de la actividad
            destinatario_id: ID del usuario (opcional)
        
        Returns:
            QuerySet de mensajes
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                actividad_id=actividad_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO]
            )
            
            if destinatario_id:
                queryset = queryset.filter(destinatario_id=destinatario_id)
            
            return queryset.order_by('-fecha_envio')
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes para actividad {actividad_id}: {str(e)}")
            raise

    @staticmethod
    def obtener_mensajes_por_proyecto(proyecto_id, destinatario_id=None):
        """
        Obtiene mensajes relacionados con un proyecto
        
        Args:
            proyecto_id: ID del proyecto
            destinatario_id: ID del usuario (opcional)
        
        Returns:
            QuerySet de mensajes
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                proyecto_id=proyecto_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO]
            )
            
            if destinatario_id:
                queryset = queryset.filter(destinatario_id=destinatario_id)
            
            return queryset.order_by('-fecha_envio')
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes para proyecto {proyecto_id}: {str(e)}")
            raise


    #Metodos para los mensajes masivos con remitente - agregados version final mensajeria
    @staticmethod
    def obtener_mensajes_enviados(remitente_id, filtros=None):
        """
        Obtiene mensajes enviados por un usuario
        
        Args:
            remitente_id: ID del usuario remitente
            filtros: Dict con filtros (destinatario_id, tipo, etc.)
        
        Returns:
            QuerySet de mensajes enviados
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                remitente_id=remitente_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO]
            )
            
            # Aplicar filtros
            if filtros:
                if filtros.get('destinatario_id'):
                    queryset = queryset.filter(destinatario_id=filtros['destinatario_id'])
                if filtros.get('tipo'):
                    queryset = queryset.filter(tipo=filtros['tipo'])
            
            # Excluir mensajes expirados
            queryset = queryset.filter(
                Q(fecha_expiracion__isnull=True) | 
                Q(fecha_expiracion__gt=timezone.now())
            )
            
            return queryset.order_by('-fecha_envio', '-prioridad')[filtros.get('offset', 0):filtros.get('offset', 0) + filtros.get('limit', 50)]
        
        except Exception as e:
            logger.error(f"Error obteniendo mensajes enviados para usuario {remitente_id}: {str(e)}")
            raise


    @staticmethod
    def contar_mensajes_enviados(remitente_id, filtros=None):
        """
        Cuenta mensajes enviados por un usuario
        
        Args:
            remitente_id: ID del usuario remitente
            filtros: Dict con filtros
        
        Returns:
            Dict con conteos
        """
        try:
            queryset = MensajeUsuario.objects.filter(
                remitente_id=remitente_id,
                estado__in=[EstadoMensaje.NO_LEIDO, EstadoMensaje.LEIDO, EstadoMensaje.ARCHIVADO]
            )
            
            # Aplicar filtros
            if filtros:
                if filtros.get('destinatario_id'):
                    queryset = queryset.filter(destinatario_id=filtros['destinatario_id'])
                if filtros.get('tipo'):
                    queryset = queryset.filter(tipo=filtros['tipo'])
            
            # Excluir expirados
            queryset = queryset.filter(
                Q(fecha_expiracion__isnull=True) | 
                Q(fecha_expiracion__gt=timezone.now())
            )
            
            # Conteo total
            total = queryset.count()
            
            # Conteo por tipo
            conteo_tipo = queryset.values('tipo').annotate(
                count=Count('id')
            )
            
            # Conteo por destinatario (top 10)
            conteo_destinatario = queryset.values('destinatario_id', 'destinatario__username').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            return {
                'total': total,
                'por_tipo': {item['tipo']: item['count'] for item in conteo_tipo},
                'por_destinatario': [
                    {
                        'destinatario_id': item['destinatario_id'],
                        'username': item['destinatario__username'],
                        'count': item['count']
                    }
                    for item in conteo_destinatario
                ]
            }
        
        except Exception as e:
            logger.error(f"Error contando mensajes enviados para usuario {remitente_id}: {str(e)}")
            raise


    @staticmethod
    def verificar_existencia_destinatarios(destinatarios_ids):
        """
        Verifica si los destinatarios existen en el sistema
        
        Args:
            destinatarios_ids: Lista de IDs de usuarios
        
        Returns:
            Tuple (existentes, inexistentes)
        """
        try:
            from spme_autenticacion.models import Usuario
            
            # Obtener usuarios existentes
            usuarios_existentes = Usuario.objects.filter(
                id__in=destinatarios_ids
            ).values_list('id', flat=True)
            
            existentes = list(usuarios_existentes)
            inexistentes = [id for id in destinatarios_ids if id not in existentes]
            
            return existentes, inexistentes
        
        except Exception as e:
            logger.error(f"Error verificando destinatarios: {str(e)}")
            raise    
                

                     
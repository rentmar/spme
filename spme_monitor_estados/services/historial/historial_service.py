# services/historial/historial_service.py
# Propósito: Servicio para registrar historial de cambios de estado
# Utiliza spme_mensajes para almacenar el historial en metadata

from django.utils import timezone
import logging

from spme_mensajes.models import MensajeUsuario, TipoMensaje

logger = logging.getLogger(__name__)

class HistorialService:
    """
    Servicio para registrar y consultar historial de cambios de estado.
    
    Cada cambio de estado queda registrado como un mensaje interno
    con metadata estructurada para facilitar consultas posteriores.
    
    El historial se almacena en la misma tabla de mensajes, pero con
    un tipo especial en metadata para diferenciarlo de notificaciones.
    """
    
    @classmethod
    def registrar_cambio(cls, tipo_entidad, entidad, cambio_info, usuario=None):
        """
        Registra un cambio de estado en el historial.
        
        Args:
            tipo_entidad: Tipo de entidad (actividad, tarea, etc.)
            entidad: La entidad que cambió de estado
            cambio_info: Diccionario con información del cambio:
                - estado_anterior
                - estado_nuevo
                - motivo
                - automatico (bool)
                - detalles (dict opcional)
            usuario: Usuario que realizó el cambio (None = sistema)
        
        Returns:
            MensajeUsuario creado o None si hay error
        """
        try:
            # Determinar destinatario (responsable de la entidad)
            destinatario = cls._obtener_responsable(tipo_entidad, entidad)
            
            # Preparar metadata estructurada para consultas futuras
            metadata = {
                'tipo_historial': 'cambio_estado',
                'tipo_entidad': tipo_entidad,
                'entidad_id': entidad.id,
                'entidad_codigo': getattr(entidad, 'codigo', ''),
                'entidad_nombre': cls._obtener_nombre(entidad),
                'estado_anterior': cambio_info.get('estado_anterior'),
                'estado_nuevo': cambio_info.get('estado_nuevo'),
                'motivo': cambio_info.get('motivo', ''),
                'automatico': cambio_info.get('automatico', True),
                'fecha_cambio': timezone.now().isoformat(),
                'detalles': cambio_info.get('detalles', {})
            }
            
            # Generar asunto según el tipo de cambio
            asunto = cls._generar_asunto(tipo_entidad, cambio_info, entidad)
            
            # Generar contenido descriptivo
            contenido = cls._generar_contenido(tipo_entidad, cambio_info, entidad)
            
            # Crear mensaje interno con la metadata
            mensaje = MensajeUsuario.objects.create(
                destinatario=destinatario if destinatario else None,
                remitente=usuario,  # None = sistema
                tipo=TipoMensaje.SISTEMA,
                prioridad=2,  # Prioridad media para historial
                icono=cls._obtener_icono(cambio_info),
                asunto=asunto,
                contenido=contenido,
                fecha_expiracion=timezone.now() + timezone.timedelta(days=365),  # 1 año
                actividad_id=entidad.id if tipo_entidad == 'actividad' else None,
                metadata=metadata
            )
            
            logger.info(f"📝 Historial registrado: {tipo_entidad} {getattr(entidad, 'codigo', '')} - "
                       f"{cambio_info.get('estado_anterior')} → {cambio_info.get('estado_nuevo')}")
            
            return mensaje
            
        except Exception as e:
            logger.error(f"❌ Error registrando historial: {e}")
            return None
    
    @classmethod
    def _obtener_responsable(cls, tipo_entidad, entidad):
        """
        Obtiene el responsable de la entidad
        """
        if tipo_entidad == 'actividad':
            return getattr(entidad, 'responsable', None)
        elif tipo_entidad == 'tarea':
            if hasattr(entidad, 'actividad') and entidad.actividad:
                return getattr(entidad.actividad, 'responsable', None)
        elif tipo_entidad == 'actividad_pei':
            return getattr(entidad, 'responsable', None)
        elif tipo_entidad == 'tarea_pei':
            if hasattr(entidad, 'actividad') and entidad.actividad:
                return getattr(entidad.actividad, 'responsable', None)
        return None
    
    @classmethod
    def _obtener_nombre(cls, entidad):
        """
        Obtiene el nombre de la entidad
        """
        return getattr(entidad, 'nombreCorto', getattr(entidad, 'titulo', ''))
    
    @classmethod
    def _generar_asunto(cls, tipo_entidad, cambio_info, entidad):
        """
        Genera asunto para el mensaje de historial
        """
        codigo = getattr(entidad, 'codigo', '')
        estado_nuevo = cambio_info.get('estado_nuevo', '')
        
        # Mapeo de estados a iconos
        iconos = {
            'EJEC': '🚀',
            'RETR': '⚠️',
            'REPROG': '📅',
            'REP': '📋',
            'FIN': '✅',
            'COMPL': '✅',
            'PLAN': '📝',
            'CRD': '🆕',
        }
        icono = iconos.get(estado_nuevo, '📊')
        
        nombres = {
            'actividad': 'Actividad',
            'tarea': 'Tarea',
            'actividad_pei': 'Actividad PEI',
            'tarea_pei': 'Tarea PEI',
        }
        nombre_tipo = nombres.get(tipo_entidad, tipo_entidad)
        
        return f"{icono} {nombre_tipo} {codigo}: {cambio_info.get('estado_anterior')} → {estado_nuevo}"
    
    @classmethod
    def _generar_contenido(cls, tipo_entidad, cambio_info, entidad):
        """
        Genera contenido descriptivo del cambio
        """
        nombre = cls._obtener_nombre(entidad)
        codigo = getattr(entidad, 'codigo', '')
        estado_anterior = cambio_info.get('estado_anterior', '')
        estado_nuevo = cambio_info.get('estado_nuevo', '')
        motivo = cambio_info.get('motivo', '')
        automatico = cambio_info.get('automatico', True)
        
        # Obtener nombre legible del tipo de entidad
        nombres = {
            'actividad': 'Actividad',
            'tarea': 'Tarea',
            'actividad_pei': 'Actividad PEI',
            'tarea_pei': 'Tarea PEI',
        }
        nombre_tipo = nombres.get(tipo_entidad, tipo_entidad)
        
        contenido = f"""
            Registro de cambio de estado - {nombre_tipo}

            • Entidad: {nombre_tipo}
            • Código: {codigo}
            • Nombre: {nombre}

            • Estado anterior: {estado_anterior}
            • Estado nuevo: {estado_nuevo}

            • Motivo: {motivo}
            • Tipo de cambio: {'Automático' if automatico else 'Manual'}
            • Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        # Agregar detalles específicos si existen
        if 'dias' in cambio_info.get('detalles', {}):
            contenido += f"\n• Días de retraso: {cambio_info['detalles']['dias']}"
        
        return contenido.strip()
    
    @classmethod
    def _obtener_icono(cls, cambio_info):
        """
        Obtiene icono según el tipo de cambio
        """
        estado_nuevo = cambio_info.get('estado_nuevo', '')
        
        iconos = {
            'EJEC': '🚀',
            'RETR': '⚠️',
            'REPROG': '📅',
            'REP': '📋',
            'FIN': '✅',
            'COMPL': '✅',
        }
        return iconos.get(estado_nuevo, '📊')
    
    @classmethod
    def obtener_historial_entidad(cls, tipo_entidad, entidad_id, limite=50):
        """
        Obtiene el historial de cambios de una entidad específica.
        
        Args:
            tipo_entidad: Tipo de entidad
            entidad_id: ID de la entidad
            limite: Número máximo de registros
            
        Returns:
            QuerySet de mensajes con el historial
        """
        return MensajeUsuario.objects.filter(
            metadata__tipo_historial='cambio_estado',
            metadata__tipo_entidad=tipo_entidad,
            metadata__entidad_id=entidad_id
        ).order_by('-fecha_envio')[:limite]
    
    @classmethod
    def obtener_historial_usuario(cls, usuario, limite=100):
        """
        Obtiene el historial de cambios de un usuario específico.
        
        Args:
            usuario: Usuario (responsable)
            limite: Número máximo de registros
            
        Returns:
            QuerySet de mensajes con el historial
        """
        return MensajeUsuario.objects.filter(
            destinatario=usuario,
            metadata__tipo_historial='cambio_estado'
        ).order_by('-fecha_envio')[:limite]
    
    @classmethod
    def obtener_historial_fechas(cls, fecha_desde, fecha_hasta, tipo_entidad=None):
        """
        Obtiene historial de cambios en un rango de fechas.
        
        Args:
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            tipo_entidad: Filtrar por tipo (opcional)
            
        Returns:
            QuerySet de mensajes
        """
        queryset = MensajeUsuario.objects.filter(
            metadata__tipo_historial='cambio_estado',
            fecha_envio__range=[fecha_desde, fecha_hasta]
        )
        
        if tipo_entidad:
            queryset = queryset.filter(metadata__tipo_entidad=tipo_entidad)
        
        return queryset.order_by('-fecha_envio')
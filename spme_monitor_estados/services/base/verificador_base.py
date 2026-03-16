# services/base/verificador_base.py
# Propósito: Clase base abstracta para todos los verificadores
# Define la interfaz común y funcionalidad compartida

from abc import ABC, abstractmethod
from django.utils import timezone
import logging



logger = logging.getLogger(__name__)

class VerificadorBase(ABC):
    """
    Clase base abstracta para todos los verificadores de estado.
    
    Esta clase define la estructura que deben seguir todos los verificadores:
    - obtener_queryset: qué entidades verificar
    - verificar_entidad: cómo verificar cada entidad
    - procesar_todas: orquesta la verificación de todas las entidades
    """
    
    def __init__(self, config):
        """
        Inicializa el verificador con su configuración específica
        
        Args:
            config: Objeto ConfiguracionMonitoreo para este tipo de entidad
        """
        self.config = config
        self.hoy = timezone.now().date()  # Fecha actual para comparaciones
        
    @abstractmethod
    def obtener_queryset(self):
        """
        Retorna el queryset de entidades a verificar.
        
        Cada verificador concreto debe implementar este método
        para definir qué entidades de su tipo serán procesadas.
        
        Returns:
            QuerySet: Las entidades a verificar
        """
        pass
    
    @abstractmethod
    def verificar_entidad(self, entidad):
        """
        Verifica una entidad individual y retorna las acciones tomadas.
        
        Este método contiene la lógica específica de negocio:
        - Verifica si la entidad debe cambiar de estado
        - Ejecuta los cambios necesarios
        - Dispara notificaciones
        - Registra historial
        
        Args:
            entidad: La entidad a verificar
            
        Returns:
            dict: Resultado de la verificación con:
                - cambio_realizado: bool
                - cambio: dict con detalles del cambio
                - notificaciones: int
                - emails_encolados: int
        """
        pass
    
    def procesar_todas(self):
        """
        Procesa todas las entidades del tipo.
        
        Este método orquesta la verificación de todas las entidades
        y recolecta estadísticas del proceso.
        
        Returns:
            dict: Estadísticas del procesamiento
        """
        # Obtener las entidades a verificar
        queryset = self.obtener_queryset()
        total = queryset.count()
        
        # Inicializar resultados
        resultados = {
            'procesadas': 0,
            'cambios': 0,
            'notificaciones': 0,
            'emails_encolados': 0,
            'detalles': []
        }
        
        logger.info(f"📊 Procesando {total} entidades")
        
        # Verificar cada entidad individualmente
        for entidad in queryset:
            try:
                # Verificar la entidad
                resultado = self.verificar_entidad(entidad)
                resultados['procesadas'] += 1
                
                # Si hubo cambios, registrar
                if resultado.get('cambio_realizado'):
                    resultados['cambios'] += 1
                    resultados['notificaciones'] += resultado.get('notificaciones', 0)
                    resultados['emails_encolados'] += resultado.get('emails_encolados', 0)
                    resultados['detalles'].append({
                        'id': entidad.id,
                        'codigo': getattr(entidad, 'codigo', ''),
                        'nombre': getattr(entidad, 'nombreCorto', getattr(entidad, 'titulo', '')),
                        'cambio': resultado.get('cambio')
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error verificando entidad {entidad.id}: {e}")
        
        # Logging de resultados
        logger.info(f"✅ Procesadas: {resultados['procesadas']}")
        logger.info(f"✅ Cambios: {resultados['cambios']}")
        logger.info(f"✅ Notificaciones: {resultados['notificaciones']}")
        logger.info(f"✅ Emails encolados: {resultados['emails_encolados']}")
        
        return resultados
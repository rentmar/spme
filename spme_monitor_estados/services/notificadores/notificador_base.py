# services/notificadores/notificador_base.py
# Propósito: Define la interfaz para todos los notificadores

from abc import ABC, abstractmethod

class NotificadorBase(ABC):
    """
    Interfaz base para todos los notificadores.
    
    Define el contrato que deben cumplir todos los notificadores:
    - notificar: método principal para enviar notificaciones
    """
    @abstractmethod
    def notificar(self, tipo_entidad, evento, entidad, contexto=None):
        """
        Método principal de notificación.
        
        Args:
            tipo_entidad: Tipo de entidad (actividad, tarea, etc.)
            evento: Evento ocurrido (inicio, retraso, etc.)
            entidad: La entidad relacionada
            contexto: Datos adicionales (días de retraso, etc.)
            
        Returns:
            Resultado de la notificación (depende del implementación)
        """
        pass
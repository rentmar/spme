from django.core.cache import cache
from .models import SystemConfig

def get_system_config():
    """Obtiene la configuración del sistema con cache"""
    config = cache.get('system_config')
    if not config:
        config = SystemConfig.get_config()
        cache.set('system_config', config, timeout=60*60)  # Cache por 1 hora
    return config

def clear_config_cache():
    """Limpia la cache de configuración"""
    cache.delete('system_config')
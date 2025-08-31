from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SystemConfig
from .services import clear_config_cache

@receiver(post_save, sender=SystemConfig)
def system_config_changed(sender, instance, **kwargs):
    """Se ejecuta cuando cambia la configuración del sistema"""
    clear_config_cache()
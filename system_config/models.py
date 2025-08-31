from django.db import models
from django.utils import timezone

class SystemConfig(models.Model):
    """Configuración global del sistema"""
    # Configuración básica
    site_name = models.CharField(max_length=100, default="Mi Aplicación")
    site_url = models.URLField(default="https://miapp.com")
    maintenance_mode = models.BooleanField(default=False)
    
    # Configuración de primera ejecución
    initialized = models.BooleanField(default=False)
    initialized_at = models.DateTimeField(null=True, blank=True)
    
    # Configuración de email
    email_host = models.CharField(max_length=100, blank=True)
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_default_from = models.EmailField(default="noreply@miapp.com")
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
    
    @classmethod
    def get_config(cls):
        """Obtiene o crea la configuración del sistema"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"Configuración del Sistema ({self.site_name})"
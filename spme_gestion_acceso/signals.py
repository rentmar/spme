#spme_gestion_acceso/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserInstanciaGestora, PermisoProyectoEspecifico
from .services.permission_service import PermissionService

@receiver([post_save, post_delete], sender=UserInstanciaGestora)
def invalidar_cache_instancias(sender, instance, **kwargs):
    permission_service = PermissionService()
    permission_service.invalidar_cache_usuario(instance.usuario_id)

@receiver([post_save, post_delete], sender=PermisoProyectoEspecifico)
def invalidar_cache_permisos(sender, instance, **kwargs):
    permission_service = PermissionService()
    permission_service.invalidar_cache_usuario(instance.usuario_id)

@receiver(post_save, sender=UserInstanciaGestora)
@receiver(post_save, sender=PermisoProyectoEspecifico)
def log_cambio_permisos(sender, instance, created, **kwargs):
    import logging
    logger = logging.getLogger('permisos')
    
    action = 'creado' if created else 'actualizado'
    logger.info(f"Permiso {action}: {instance}")
"""
Señales para actualización automática del ejecutado.

Cuando una solicitud cambia su estado de aprobación,
se recalcula el ejecutado de la actividad asociada.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso,
    SolicitudViaje,
    SolicitudPagoDirecto,
)
from spme_actividades.models import (
    Actividad,
)

from spme_presupuesto.repositories.ejecucion_repository import EjecucionRepository

def actualizar_ejecutado_actividad(actividad_id):
    """
    Recalcula totalEjecutado, saldo y gradoEjecucion de una actividad.
    """
    if not actividad_id:
        return

    try:
        actividad = Actividad.objects.get(id=actividad_id)
    except Actividad.DoesNotExist:
        return

    total_ejecutado = EjecucionRepository.total_ejecutado_actividad(actividad_id)
    presupuesto = float(actividad.presupuesto or 0)

    Actividad.objects.filter(pk=actividad.pk).update(
        totalEjecutado=total_ejecutado,
        saldo=presupuesto - total_ejecutado,
        gradoEjecucion=(
            f"{round((total_ejecutado / presupuesto * 100), 2)}%"
            if presupuesto > 0
            else "0%"
        )
    )

@receiver(post_save, sender=SolicitudFondos)
def actualizar_al_guardar_fondos(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_save, sender=SolicitudReembolso)
def actualizar_al_guardar_reembolso(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_save, sender=SolicitudViaje)
def actualizar_al_guardar_viaje(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_save, sender=SolicitudPagoDirecto)
def actualizar_al_guardar_pago_directo(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_delete, sender=SolicitudFondos)
def actualizar_al_eliminar_fondos(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_delete, sender=SolicitudReembolso)
def actualizar_al_eliminar_reembolso(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_delete, sender=SolicitudViaje)
def actualizar_al_eliminar_viaje(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)


@receiver(post_delete, sender=SolicitudPagoDirecto)
def actualizar_al_eliminar_pago_directo(sender, instance, **kwargs):
    if instance.actividad_id:
        actualizar_ejecutado_actividad(instance.actividad_id)

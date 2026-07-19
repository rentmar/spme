# spme/spme_email/repositories/solicitud_repository.py
from typing import List
from django.contrib.auth import get_user_model

User = get_user_model()

class SolicitudRepository:
    """
    Consultas a BD para el módulo de notificaciones.
    """

    @staticmethod
    def get_solicitud_fondos(solicitud_id: int):
        from spme_monitoreo.models import SolicitudFondos
        return SolicitudFondos.objects.select_related(
            'usuario', 'actividad', 'tarea', 'contador', 'coordinador'
        ).get(id=solicitud_id)
    
    @staticmethod
    def get_solicitud_reembolso(solicitud_id: int):
        from spme_monitoreo.models import SolicitudReembolso
        return SolicitudReembolso.objects.select_related(
            'usuario', 'actividad', 'tarea', 'responsable', 'coordinador'
        ).get(id=solicitud_id)
    
    @staticmethod
    def get_solicitud_viaje(solicitud_id: int):
        from spme_monitoreo.models import SolicitudViaje
        return SolicitudViaje.objects.select_related(
            'usuario', 'actividad', 'tarea', 'responsable', 'coordinador'
        ).get(id=solicitud_id)
    
    @staticmethod
    def get_solicitud_pago_directo(solicitud_id: int):
        from spme_monitoreo.models import SolicitudPagoDirecto
        return SolicitudPagoDirecto.objects.select_related(
            'usuario', 'actividad', 'tarea', 'contador', 'coordinador'
        ).get(id=solicitud_id)
    
    @staticmethod
    def get_rendicion_cuentas(rendicion_id: int):
        from spme_monitoreo.models import RendicionCuentas
        return RendicionCuentas.objects.select_related(
            'usuario', 'actividad', 'tarea', 'responsable',
            'coordinador', 'contador', 'administrador'
        ).get(id=rendicion_id)
    
    @staticmethod
    def get_usuarios_por_ids(usuarios_ids: List[int]) -> List[dict]:
        """Obtiene usuarios por sus IDs. Retorna lista con id, nombre, correo."""
        usuarios = User.objects.filter(
            id__in=usuarios_ids
        ).values('id', 'nombre', 'paterno', 'materno', 'correo')
        return [
            {
                'id': u['id'],
                'nombre': f"{u['nombre']} {u['paterno']} {u['materno']}".strip() or f"Usuario {u['id']}",
                'email': u['correo'],
            }
            for u in usuarios
        ]
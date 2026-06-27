from django.apps import AppConfig


class SpmePresupuestoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spme_presupuesto'
    verbose_name = 'Presupuesto-planificacion-ejecucion'

    def ready(self):
        import spme_presupuesto.signals



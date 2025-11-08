from django.apps import AppConfig


class SpmeGestionAccesoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spme_gestion_acceso'
    verbose_name = 'Gestion de Acceso SPME'

    def ready(self):
        import spme_gestion_acceso.signals

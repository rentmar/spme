from django.urls import path
from .views import (check_setup_status, run_migrations, create_admin_user, system_config, toggle_maintenance_mode, check_connection)


urlpatterns = [
    # Endpoints del Wizard
    path('wizard/check-status/', check_setup_status, name='wizard-check-status'),
    path('wizard/run-migrations/', run_migrations, name='wizard-run-migrations'),
    path('wizard/create-admin/', create_admin_user, name='wizard-create-admin'),
    
    # Configuración del sistema
    path('config/', system_config, name='system-config'),
    path('config/toggle-maintenance/', toggle_maintenance_mode, name='toggle-maintenance'),

    #Check de conexion
    path('check-connection/', check_connection, name='check_connection'),
]

import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\proyecto_smpe\spme')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from spme_monitoreo.models import SolicitudFondos

try:
    # ID from the previous test run output
    solicitud_id = 75 
    solicitud = SolicitudFondos.objects.get(id=solicitud_id)
    
    print(f"Solicitud ID: {solicitud.id}")
    print(f"Contador ID saved: {solicitud.contador_id}")
    
    if solicitud.contador_id == 64:
        print("SUCCESS: Contador ID matched expected value (64).")
    else:
        print(f"FAILURE: Expected 64, got {solicitud.contador_id}")

except SolicitudFondos.DoesNotExist:
    print(f"Solicitud {solicitud_id} not found.")
except Exception as e:
    print(f"Error: {e}")

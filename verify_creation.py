import os
import django
import json

from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad
from rest_framework.test import APIClient

def verify():
    print("Setting up test data...")
    
    # Get or create dependencies
    forma_pago, _ = FormaPago.objects.get_or_create(codigo='EF', defaults={'formaPago': 'Efectivo'})
    
    # We need a user. Assuming one exists or creating a dummy one.
    # Note: Password hashing might be needed if we were logging in, but we are just using the ID for FK.
    usuario, _ = Usuario.objects.get_or_create(
        username='testuser', 
        defaults={'nombre': 'Test', 'paterno': 'User', 'ci': '1234567'}
    )
    
    actividad, _ = Actividad.objects.get_or_create(
        codigo='ACT-001',
        defaults={'nombreCorto': 'Actividad de prueba'}
    )

    print(f"Using IDs: FormaPago={forma_pago.id}, Usuario={usuario.id}, Actividad={actividad.id}")

    # Construct payload
    payload = {
        "detalle_destino_fondos": {
            "items": [
                {"concepto": "Transporte", "monto": 100.00, "partida_sf": "101"},
                {"concepto": "Alimentacion", "monto": 50.00, "partida_sf": "102"}
            ]
        },
        "forma_pago": forma_pago.id,
        "lugar_solicitud": "La Paz",
        "fecha_solicitud": str(date.today()),
        "monto_solicitado": 150.00,
        "id_responsable": usuario.id,
        "id_coordinador": usuario.id,
        "id_usuario": usuario.id,
        "id_actividad": actividad.id,
        "descripcionActividad": "Verificacion de sistema",
        "objetivoActividad": "Probar endpoint",
        "datosFormaPago": {"banco": "TestBank", "cuenta": "12345"},
        "bloquear_iconos_sol_fondos": False
    }

    print("Sending POST request to /monitoreo_api/crearSolicitudFondos/...")
    
    # Using Django Test Client to avoid running server issues or auth headers if not needed for this specific check
    # But user asked to verify the ENDPOINT.
    # If the endpoint requires auth, we might need to handle that. 
    # Based on views.py, there are no permission_classes set, so it might be open or default.
    
    client = APIClient()
    response = client.post(
        '/monitoreo_api/crearSolicitudFondos/',
        data=payload,
        format='json'
    )

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.data}")

    if response.status_code == 201:
        print("Request successful. Verifying Database...")
        
        # Check DB
        # The response should contain the ID or data.
        # Let's query the latest one.
        latest_solicitud = SolicitudFondos.objects.last()
        
        if latest_solicitud:
            print(f"Found SolicitudFondos in DB: ID={latest_solicitud.id}")
            print(f"Monto: {latest_solicitud.montoSolicitado}")
            print(f"Lugar: {latest_solicitud.lugarSolicitud}")
            print(f"Descripcion: {latest_solicitud.descripcion_actividad}")
            print(f"Objetivo: {latest_solicitud.objetivo_actividad}")
            print(f"Datos Pago: {latest_solicitud.datos_forma_pago}")
            
            if (latest_solicitud.montoSolicitado == 150.00 and 
                latest_solicitud.lugarSolicitud == "La Paz" and
                latest_solicitud.descripcion_actividad == "Verificacion de sistema" and
                latest_solicitud.objetivo_actividad == "Probar endpoint" and
                latest_solicitud.datos_forma_pago == {"banco": "TestBank", "cuenta": "12345"}):
                print("VERIFICATION SUCCESS: Data matches payload.")
            else:
                print("VERIFICATION FAILED: Data mismatch.")
        else:
            print("VERIFICATION FAILED: No record found in DB.")
            
    else:
        print("VERIFICATION FAILED: Endpoint returned error.")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"An error occurred: {e}")

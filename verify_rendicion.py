import os
import django
from datetime import date
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from spme_monitoreo.models import RendicionCuentas
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad
from rest_framework.test import APIClient

def verify():
    print("Setting up test data for Rendicion Cuentas...")
    
    # Create or get a user
    usuario, _ = Usuario.objects.get_or_create(
        username='testuser_rc', 
        defaults={'nombre': 'Test', 'paterno': 'User', 'ci': '999999'}
    )
    
    # Create or get an activity
    actividad, _ = Actividad.objects.get_or_create(
        codigo='ACT-RC-TEST',
        defaults={'nombreCorto': 'Actividad RC Test'}
    )

    print(f"Using Usuario={usuario.id}, Actividad={actividad.id}")

    # Construct payload
    # Including the fields we fixed: montoAsignado and fechaActividad
    test_monto_asignado = 1500.50
    test_fecha_actividad = str(date.today())
    
    payload = {
        "numeroFormulario": "RC-TEST-001",
        "montoDescargado": 500.00,
        "detalleDestinoFondos": [],
        "idresponsable": usuario.id,
        "idActividad": actividad.id,
        "fechaActividad": test_fecha_actividad, 
        "montoAsignado": test_monto_asignado,
        "descripcionActividad": "Verificacion RC",
        "lugarActividad": "Oficina Central"
    }

    print("Sending POST request to /api/monitoreo/crear-rendicion-cuentas/...")
    
    client = APIClient()
    client.force_authenticate(user=usuario)
    
    response = client.post(
        '/api/monitoreo/crear-rendicion-cuentas/',
        data=payload,
        format='json'
    )

    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.data}")

    if response.status_code == 201:
        print("Request successful. Verifying Database...")
        
        # Get the ID from response or query last
        rc_id = response.data.get('id')
        if rc_id:
            rendicion = RendicionCuentas.objects.get(id=rc_id)
        else:
            rendicion = RendicionCuentas.objects.last()
        
        if rendicion:
            print(f"Found RendicionCuentas in DB: ID={rendicion.id}")
            print(f"Monto Asignado (DB): {rendicion.montoAsignado} (Expected: {test_monto_asignado})")
            print(f"Fecha Actividad (DB): {rendicion.fechaActividad} (Expected: {test_fecha_actividad})")
            
            # Decimal comparison
            db_monto = rendicion.montoAsignado
            expected_monto = Decimal(str(test_monto_asignado))
            
            # Date comparison
            db_fecha = str(rendicion.fechaActividad)
            expected_fecha = test_fecha_actividad

            # Numero Formulario Comparison
            expected_numero = f"FRC-{rendicion.id}"
            db_numero = rendicion.numeroFormulario
            
            # Fecha Rendicion Comparison (should be today)
            db_fecha_rendicion = str(rendicion.fechaRendicion)
            expected_fecha_rendicion = str(date.today())

            if (db_monto == expected_monto and 
                db_fecha == expected_fecha and 
                db_numero == expected_numero and
                db_fecha_rendicion == expected_fecha_rendicion):
                print("VERIFICATION SUCCESS: Data matches payload, ID rule, and Date rule.")
            else:
                print("VERIFICATION FAILED: Data mismatch.")
                if db_monto != expected_monto:
                    print(f"Mismatch in Monto Asignado: {db_monto} != {expected_monto}")
                if db_fecha != expected_fecha:
                    print(f"Mismatch in Fecha Actividad: {db_fecha} != {expected_fecha}")
                if db_numero != expected_numero:
                    print(f"Mismatch in Numero Formulario: {db_numero} != {expected_numero}")
                if db_fecha_rendicion != expected_fecha_rendicion:
                    print(f"Mismatch in Fecha Rendicion: {db_fecha_rendicion} != {expected_fecha_rendicion}")
            
    else:
        print("VERIFICATION FAILED: Endpoint returned error.")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"An error occurred: {e}")

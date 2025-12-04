import os
import django
import json
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from spme_monitoreo.models import SolicitudFondos, FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad
from rest_framework.test import APIClient

def verify_retrieval():
    print("Setting up test data for retrieval verification...")
    
    # Get or create dependencies
    forma_pago, _ = FormaPago.objects.get_or_create(codigo='EF', defaults={'formaPago': 'Efectivo'})
    
    usuario, _ = Usuario.objects.get_or_create(
        username='testuser_retrieval', 
        defaults={'nombre': 'Test', 'paterno': 'User', 'ci': '9999999'}
    )
    
    actividad, _ = Actividad.objects.get_or_create(
        codigo='ACT-RETRIEVAL',
        defaults={'nombreCorto': 'Actividad de prueba retrieval'}
    )

    # Create a SolicitudFondos directly in DB with known values
    solicitud = SolicitudFondos.objects.create(
        detalleDestinoFondos={"items": [{"concepto": "Test", "monto": 100}]},
        formaPago_id=forma_pago.id,
        lugarSolicitud="Cochabamba",
        fechaSolicitud=date.today(),
        montoSolicitado=200.00,
        responsable_id=usuario.id,
        coordinador_id=usuario.id,
        usuario_id=usuario.id,
        actividad_id=actividad.id,
        descripcion_actividad="Descripcion para verificar retrieval",
        objetivo_actividad="Objetivo para verificar retrieval",
        datos_forma_pago={"banco": "BancoSol", "cuenta": "987654321"},
        bloquearIconosSolFondos=False
    )
    
    print(f"Created SolicitudFondos with ID: {solicitud.id}")

    print("Sending GET request to /monitoreo_api/obtenerSolicitudFondos/...")
    
    client = APIClient()
    response = client.get('/monitoreo_api/obtenerSolicitudFondos/')

    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        solicitudes = data.get('solicitudes', [])
        
        # Find our created solicitud
        found_solicitud = next((s for s in solicitudes if s['id'] == solicitud.id), None)
        
        if found_solicitud:
            print(f"Found Solicitud ID {solicitud.id} in response.")
            
            # Check fields
            desc = found_solicitud.get('descripcion_actividad')
            obj = found_solicitud.get('objetivo_actividad')
            datos_pago = found_solicitud.get('datos_forma_pago')
            
            print(f"descripcion_actividad: {desc}")
            print(f"objetivo_actividad: {obj}")
            print(f"datos_forma_pago: {datos_pago}")
            
            if (desc == "Descripcion para verificar retrieval" and
                obj == "Objetivo para verificar retrieval" and
                datos_pago == {"banco": "BancoSol", "cuenta": "987654321"}):
                print("VERIFICATION SUCCESS: All fields are present and correct.")
            else:
                print("VERIFICATION FAILED: Fields mismatch or missing.")
        else:
            print("VERIFICATION FAILED: Created solicitud not found in response.")
    else:
        print(f"VERIFICATION FAILED: Endpoint returned error: {response.data}")

if __name__ == "__main__":
    try:
        verify_retrieval()
    except Exception as e:
        print(f"An error occurred: {e}")

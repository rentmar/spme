"""
Script para probar el endpoint con un payload exactamente como lo enviaría el frontend
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from rest_framework.test import APIClient
from datetime import date

# Simular payload del frontend con camelCase
payload_frontend = {
    "detalle_destino_fondos": {
        "items": [
            {"concepto": "Transporte", "monto": 100.00, "partida_sf": "101"},
            {"concepto": "Alimentacion", "monto": 50.00, "partida_sf": "102"}
        ]
    },
    "forma_pago": 4,
    "lugar_solicitud": "La Paz",
    "fecha_solicitud": str(date.today()),
    "monto_solicitado": 150.00,
    "id_responsable": 65,
    "id_coordinador": 65,
    "id_usuario": 65,
    "id_actividad": 43,
    "descripcionActividad": "Test desde frontend",
    "objetivoActividad": "Verificar camelCase",
    "datosFormaPago": {"banco": "BancoTest", "cuenta": "99999"},
    "bloquear_iconos_sol_fondos": False
}

print("=" * 80)
print("PRUEBA CON PAYLOAD FRONTEND (camelCase)")
print("=" * 80)

client = APIClient()
response = client.post(
    '/monitoreo_api/crearSolicitudFondos/',
    data=payload_frontend,
    format='json'
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Body: {response.data}")

if response.status_code == 201:
    from spme_monitoreo.models import SolicitudFondos
    solicitud_id = response.data.get('id')
    solicitud = SolicitudFondos.objects.get(id=solicitud_id)
    
    print(f"\n✓ Solicitud creada con ID: {solicitud_id}")
    print(f"  - descripcion_actividad: {solicitud.descripcion_actividad}")
    print(f"  - objetivo_actividad: {solicitud.objetivo_actividad}")
    print(f"  - datos_forma_pago: {solicitud.datos_forma_pago}")
    
    if (solicitud.descripcion_actividad == "Test desde frontend" and
        solicitud.objetivo_actividad == "Verificar camelCase" and
        solicitud.datos_forma_pago == {"banco": "BancoTest", "cuenta": "99999"}):
        print("\n✅ ÉXITO: Todos los campos se guardaron correctamente con camelCase")
    else:
        print("\n❌ ERROR: Los campos no se guardaron correctamente")
        print(f"   Esperado descripcion: 'Test desde frontend', Obtenido: '{solicitud.descripcion_actividad}'")
        print(f"   Esperado objetivo: 'Verificar camelCase', Obtenido: '{solicitud.objetivo_actividad}'")
        print(f"   Esperado datos_pago: {{'banco': 'BancoTest', 'cuenta': '99999'}}, Obtenido: {solicitud.datos_forma_pago}")
else:
    print(f"\n❌ ERROR: El endpoint retornó {response.status_code}")

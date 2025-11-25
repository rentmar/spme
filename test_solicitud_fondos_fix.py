"""
Script para probar el endpoint de crear solicitud de fondos
con los campos descripcion_actividad, objetivo_actividad y datos_forma_pago
"""
import requests
import json

# URL del endpoint
url = "http://127.0.0.1:8000/api/monitoreo/crear-solicitud-fondos/"

# Payload de prueba (el mismo que proporcionaste)
payload = {
    "numero_formulario": "SF-2024-TEST",
    "detalle_destino_fondos": {
        "items": [
            {
                "concepto": "Materiales de oficina",
                "monto": 150.00,
                "partida_sf": "1.1.1.01"
            }
        ]
    },
    "forma_pago": 1,
    "lugar_solicitud": "La Paz",
    "fecha_solicitud": "2024-01-15",
    "fecha_realizacion_actividad": "2024-01-20",
    "monto_solicitado": 225.50,
    "validacion_responsable": False,
    "id_responsable": None,
    "validacion_coordinador": False,
    "id_coordinador": 64,
    "id_usuario": 64,
    "id_actividad": 1,
    "id_tarea": None,
    "descripcion_actividad": "Reunión de coordinación del proyecto",
    "objetivo_actividad": "Coordinar las actividades del primer trimestre",
    "datos_forma_pago": {
        "banco": "Banco Unión",
        "cuenta": "123456789",
        "tipo_cuenta": "corriente"
    },
    "bloquear_iconos_sol_fondos": True
}

# Hacer la petición POST
print("Enviando petición POST a:", url)
print("Payload:", json.dumps(payload, indent=2))
print("\n" + "="*80 + "\n")

try:
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("\nResponse Body:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200 or response.status_code == 201:
        print("\n✅ Solicitud creada exitosamente!")
        response_data = response.json()
        if 'data' in response_data and 'id' in response_data['data']:
            solicitud_id = response_data['data']['id']
            print(f"\n📋 ID de la solicitud creada: {solicitud_id}")
            print("\nVerifica en la base de datos que los siguientes campos se guardaron:")
            print("  - descripcion_actividad: 'Reunión de coordinación del proyecto'")
            print("  - objetivo_actividad: 'Coordinar las actividades del primer trimestre'")
            print("  - datos_forma_pago: {'banco': 'Banco Unión', 'cuenta': '123456789', 'tipo_cuenta': 'corriente'}")
    else:
        print("\n❌ Error al crear la solicitud")
        
except requests.exceptions.ConnectionError:
    print("❌ Error: No se pudo conectar al servidor. Asegúrate de que el servidor Django esté corriendo.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

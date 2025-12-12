"""
Script para probar el endpoint de crear solicitud de fondos con contador_id (nuevo nombre de campo)
"""
import json
import urllib.request
import urllib.error

def get_json(url):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

# 1. Buscar un proyecto con actividades
print("Buscando proyecto con actividades...")
actividad_id = 1 # Default
try:
    proyectos = get_json("http://127.0.0.1:8000/api/proyectos/")
    if proyectos:
        for proj in proyectos:
            pid = proj['id']
            try:
                actividades = get_json(f"http://127.0.0.1:8000/api/actividades/proyecto/{pid}/")
                if actividades and len(actividades) > 0:
                    actividad_id = actividades[0]['id']
                    break
            except:
                pass
except:
    pass

# URL
url = "http://127.0.0.1:8000/api/monitoreo/crear-solicitud-fondos/"

# Payload with contador_id
payload = {
    "numero_formulario": "SF-2024-TEST-CONTADOR-FIELD",
    "detalle_destino_fondos": {
        "items": [{"concepto": "Test Contador Field", "monto": 100.00}]
    },
    "forma_pago": 1,
    "lugar_solicitud": "Test",
    "fecha_solicitud": "2024-01-15",
    "monto_solicitado": 100.00,
    "validacion_responsable": False,
    # "id_responsable": 64,  <-- OLD
    "contador_id": 64,     # <-- NEW FIELD NAME
    "validacion_coordinador": False,
    "id_coordinador": 64,
    "id_usuario": 64,
    "id_actividad": 25, # Using 25 as found in previous step
    "bloquear_iconos_sol_fondos": True
}

print("\nEnviando petición POST a:", url)
print("Payload:", json.dumps(payload, indent=2))

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        body = json.loads(response.read().decode('utf-8'))
        
        print(f"Status Code: {status_code}")
        print("Response:", json.dumps(body, indent=2))
        
        if status_code in [200, 201]:
             print("SUCCESS: Request created successfully.")

except urllib.error.HTTPError as e:
    print(f"Error HTTP {e.code}: {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")

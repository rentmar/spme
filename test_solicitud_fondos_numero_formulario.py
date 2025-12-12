
import json
import urllib.request
import urllib.error

# 1. Buscar un proyecto con actividades
print("Buscando proyecto con actividades...")
actividad_id = 1 # Default
try:
    proyectos_url = "http://127.0.0.1:8000/api/proyectos/"
    req = urllib.request.Request(proyectos_url, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        proyectos = json.loads(response.read().decode('utf-8'))
        
    if proyectos:
        for proj in proyectos:
            pid = proj['id']
            try:
                actividades_url = f"http://127.0.0.1:8000/api/actividades/proyecto/{pid}/"
                req_act = urllib.request.Request(actividades_url, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req_act) as response_act:
                    actividades = json.loads(response_act.read().decode('utf-8'))
                    if actividades and len(actividades) > 0:
                        actividad_id = actividades[0]['id']
                        break
            except:
                pass
except:
    pass

# URL
url = "http://127.0.0.1:8000/api/monitoreo/crear-solicitud-fondos/"

# Payload WITHOUT numero_formulario (to trigger auto-generation)
payload = {
    # "numero_formulario": "SF-SHOULD-NOT-BE-USED", 
    "detalle_destino_fondos": {
        "items": [{"concepto": "Test Auto Number", "monto": 50.00}]
    },
    "forma_pago": 1,
    "lugar_solicitud": "Test Auto Gen",
    "fecha_solicitud": "2024-02-01",
    "monto_solicitado": 50.00,
    "validacion_responsable": False,
    "contador_id": 64, 
    "validacion_coordinador": False,
    "id_coordinador": 64,
    "id_usuario": 64,
    "id_actividad": 25,
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
             created_id = body.get('id')
             created_num = body.get('numero_formulario')
             expected_num = f"SF-{created_id:04d}"
             
             print(f"Created ID: {created_id}")
             print(f"Created Num: {created_num}")
             print(f"Expected Num: {expected_num}")
             
             if created_num == expected_num:
                 print("SUCCESS: numero_formulario matches SF-{id}.")
             else:
                 print("FAILURE: numero_formulario does not match expected format.")

except urllib.error.HTTPError as e:
    print(f"Error HTTP {e.code}: {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")

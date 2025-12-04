"""
Script para probar el endpoint de crear solicitud de fondos
con los campos descripcion_actividad, objetivo_actividad y datos_forma_pago
Usando urllib para evitar dependencias externas.
"""
import json
import urllib.request
import urllib.error

# Función auxiliar para hacer GET
def get_json(url):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

# 1. Buscar un proyecto con actividades
print("Buscando proyecto con actividades...")
actividad_id = 1 # Default fallback
try:
    proyectos = get_json("http://127.0.0.1:8000/api/proyectos/")
    if not proyectos:
        print("No se encontraron proyectos.")
    else:
        found = False
        for proj in proyectos:
            pid = proj['id']
            print(f"Revisando proyecto {pid}...")
            try:
                actividades = get_json(f"http://127.0.0.1:8000/api/actividades/proyecto/{pid}/")
                if actividades and len(actividades) > 0:
                    actividad_id = actividades[0]['id']
                    print(f"Encontrada Actividad ID: {actividad_id} en Proyecto {pid}")
                    found = True
                    break
            except Exception as e:
                print(f"Error revisando proyecto {pid}: {e}")
        
        if not found:
            print("No se encontraron actividades en ninguno de los proyectos revisados.")

except Exception as e:
    print(f"Error al obtener datos previos: {e}")
    print("Usando ID 1 como fallback.")

# URL del endpoint
url = "http://127.0.0.1:8000/api/monitoreo/crear-solicitud-fondos/"

# Payload de prueba
payload = {
    "numero_formulario": "SF-2024-TEST-FIX-V5",
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
    "id_actividad": actividad_id,
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
print("\nEnviando petición POST a:", url)
print("Payload:", json.dumps(payload, indent=2))
print("\n" + "="*80 + "\n")

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        response_body = response.read().decode('utf-8')
        response_json = json.loads(response_body)
        
        print(f"Status Code: {status_code}")
        print("\nResponse Body:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        
        if status_code == 200 or status_code == 201:
            print("\nSolicitud creada exitosamente!")
            
            # Verificar si la respuesta contiene los datos esperados
            if 'actividad_id' in response_json:
                 print(f"  - actividad_id devuelto: {response_json['actividad_id']}")
                 if response_json['actividad_id'] == actividad_id:
                     print(f"  actividad_id coincide con el enviado ({actividad_id})")
                 else:
                     print("  actividad_id NO coincide con el enviado")
            
            print("\nVerifica en la base de datos que los siguientes campos se guardaron:")
            print("  - descripcion_actividad: 'Reunión de coordinación del proyecto'")
            print("  - objetivo_actividad: 'Coordinar las actividades del primer trimestre'")
            print("  - datos_forma_pago: {'banco': 'Banco Unión', 'cuenta': '123456789', 'tipo_cuenta': 'corriente'}")

except urllib.error.HTTPError as e:
    print(f"Error HTTP {e.code}: {e.reason}")
    try:
        print(e.read().decode('utf-8'))
    except:
        pass
except urllib.error.URLError as e:
    print(f"Error de conexión: {e.reason}")
    print("Asegúrate de que el servidor Django esté corriendo.")
except Exception as e:
    print(f"Error inesperado: {e}")

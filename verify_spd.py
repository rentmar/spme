import os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spme.settings")
django.setup()

from spme_monitoreo.dataaccess.solicitudPagoDirectoDataAccess import SolicitudPagoDirectoDataAccess
from spme_monitoreo.models import FormaPago
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad

# 1. Setup
try:
    forma_pago, _ = FormaPago.objects.get_or_create(id=1, defaults={'formaPago': 'Efectivo'})
    usuario, _ = Usuario.objects.get_or_create(id=1, defaults={'username': 'testuser'})
    actividad, _ = Actividad.objects.get_or_create(id=777, defaults={'codigo': 'ACT-SPD-777'})
    if actividad.codigo != 'ACT-SPD-777':
        actividad.codigo = 'ACT-SPD-777'
        actividad.save()

except Exception as e:
    print(f"Setup error: {e}")
    exit(1)

# 2. Payload
data = {
    'detalleDestinoFondos': {'items': []},
    'formaPago_id': 1,
    'lugarSolicitud': 'SPD Test Lab',
    'fechaSolicitud': datetime.date.today(),
    'fechaRealizacionActividad': datetime.date.today(),
    'montoSolicitado': 200.0,
    'validacionResponsable': False,
    'contador_id': 1,
    'validacionCoordinador': False,
    'coordinador_id': 1,
    'usuario_id': 1,
    'actividad_id': 777,
    'tarea_id': None,
    'descripcion_actividad': 'SPD Test Desc',
    'objetivo_actividad': 'SPD Test Obj',
    'datos_forma_pago': {},
    'bloquearIconosSolFondos': True,
    # 'numeroFormulario': 'IGNORE_ME'
}

# 3. Execute
dao = SolicitudPagoDirectoDataAccess()
try:
    print("Creating SolicitudPagoDirecto...")
    result = dao.crearSolicitudPagoDirecto(data)
    print(f"Created ID: {result.id}")
    print(f"Generated Numero: {result.numeroFormulario}")
    
    expected = f"ACT-SPD-777 - SPD {result.id:05d}"
    if result.numeroFormulario == expected:
        print("SUCCESS: Format correct.")
    else:
        print(f"FAILURE: Expected '{expected}', got '{result.numeroFormulario}'")

except Exception as e:
    print(f"Execution Error: {e}")

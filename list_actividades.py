import os
import django
import sys

# Configurar el entorno de Django
sys.path.append('d:\\proyecto_smpe\\spme')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spme.settings')
django.setup()

from spme_actividades.models import Actividad

print("Listando Actividades disponibles:")
actividades = Actividad.objects.all()[:5]
if not actividades:
    print("No hay actividades en la base de datos.")
else:
    for act in actividades:
        print(f"ID: {act.id}, Descripción: {act.descripcion}")

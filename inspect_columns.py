import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spme.settings")
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE spme_monitoreo_solicitudpagodirecto;")
    columns = [col[0] for col in cursor.fetchall()]
    print("Columns in spme_monitoreo_solicitudpagodirecto:")
    for col in columns:
        print(f"- {col}")

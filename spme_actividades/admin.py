from django.contrib import admin
from .models import Actividad, TareaActividad, TipoActividad

# Register your models here.
admin.site.register(Actividad)
admin.site.register(TareaActividad)
admin.site.register(TipoActividad)
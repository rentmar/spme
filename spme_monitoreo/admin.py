from django.contrib import admin
from .models import SolicitudFondos, RendicionCuentas, SolicitudReembolso, SolicitudViaje, SolicitudPagoDirecto, FormaPago

# Register your models here.
admin.site.register(FormaPago)
admin.site.register(SolicitudFondos)
admin.site.register(RendicionCuentas)
admin.site.register(SolicitudReembolso)
admin.site.register(SolicitudViaje)
admin.site.register(SolicitudPagoDirecto)
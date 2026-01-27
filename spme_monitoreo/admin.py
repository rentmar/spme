from django.contrib import admin
from .models import SolicitudFondos, RendicionCuentas, SolicitudReembolso, SolicitudViaje, SolicitudPagoDirecto, FormaPago, InformeActividad, InfActividad, InfTarea
from .models import (
    SolicitudFondosActPei,
    RendicionCuentasActPei,
    SolicitudReembolsoActPei,
    SolicitudViajeActPei,
    SolicitudPagoDirectoActPei,
    InformeActividadPrincipal
)
#Formas de pago
admin.site.register(FormaPago)

#Solicitudes proyecto
admin.site.register(SolicitudFondos)
admin.site.register(RendicionCuentas)
admin.site.register(SolicitudReembolso)
admin.site.register(SolicitudViaje)
admin.site.register(SolicitudPagoDirecto)


#SOLICITUDES DEL PEI
admin.site.register(SolicitudFondosActPei)
admin.site.register(RendicionCuentasActPei)
admin.site.register(SolicitudReembolsoActPei)
admin.site.register(SolicitudViajeActPei)
admin.site.register(SolicitudPagoDirectoActPei)

#Informes de actividad
#admin.site.register(InformeActividad)
admin.site.register(InfActividad)
admin.site.register(InfTarea)

admin.site.register(InformeActividadPrincipal)

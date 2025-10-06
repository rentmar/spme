from django.contrib import admin
from .models import (
    BitacoraIndicadorBase,
    BitacoraIndicadorOE,
    BitacoraIndicadorOG,
    BitacoraIndicadorROE,
    BitacoraIndicadorROG
)

# Register your models here.
admin.site.register(BitacoraIndicadorBase)
admin.site.register(BitacoraIndicadorOE)
admin.site.register(BitacoraIndicadorOG)
admin.site.register(BitacoraIndicadorROE)
admin.site.register(BitacoraIndicadorROG)
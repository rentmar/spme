from rest_framework import serializers
from spme_monitoreo.models import (
    RendicionCuentas,
    SolicitudReembolso,
    SolicitudViaje,
    SolicitudPagoDirecto,
    SolicitudFondos 
    )


#Solicitud de fondos
class SolicitudFondosResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = '__all__'

#Solicitud Reembolso
class SolicitudReembolsoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReembolso
        fields = '__all__'

#Solicitud de viaje
class SolicitudViajeResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudViaje
        fields = '__all__'

#Solicitud pago directo
class SolicitudPagoDirectoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirecto
        fields = '__all__'

#Rendicion de cuentas
class RendicionConSolicitudesSerializer(serializers.ModelSerializer):
    solicitudFondos = SolicitudFondosResumenSerializer(read_only=True)
    solicitudReembolso = SolicitudReembolsoResumenSerializer(read_only=True)
    solicitudViaje = SolicitudViajeResumenSerializer(read_only=True)
    solicitudPagoDirecto = SolicitudPagoDirectoResumenSerializer(read_only=True)
    # Mostrar IDs y nombres de usuarios relacionados
    usuario_nombre = serializers.SerializerMethodField()
    coordinador_nombre = serializers.SerializerMethodField()
    contador_nombre = serializers.SerializerMethodField()
    administrador_nombre = serializers.SerializerMethodField()

    class Meta:
        model = RendicionCuentas
        fields = '__all__'

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f"{obj.usuario.nombre} {obj.usuario.paterno} {obj.usuario.materno}".strip()
        return None

    def get_coordinador_nombre(self, obj):
        if obj.coordinador:
            return f"{obj.coordinador.nombre} {obj.coordinador.paterno} {obj.coordinador.materno}".strip()
        return None

    def get_contador_nombre(self, obj):
        if obj.contador:
            return f"{obj.contador.nombre} {obj.contador.paterno} {obj.contador.materno}".strip()
        return None

    def get_administrador_nombre(self, obj):
        if obj.administrador:
            return f"{obj.administrador.nombre} {obj.administrador.paterno} {obj.administrador.materno}".strip()
        return None

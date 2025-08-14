from rest_framework import serializers
from spme_monitoreo.models import FormaPago, SolicitudFondos, RendicionCuentas, SolicitudReembolso,SolicitudViaje, SolicitudPagoDirecto


#Forma de Pago
class FormPagoSer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = '__all__'

#Solicitud de Fondos
class SolicitudFondosSer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudFondos
        fields = '__all__'

#Rendicion de cuentas
class RendicionCuentasSer(serializers.ModelSerializer):
    class Meta:
        model = RendicionCuentas
        fields = '__all__'        

#Solicitude de Reembolso
class SolicitudReemboldoSer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReembolso
        fields = '__all__'

#Solicitud de viaje
class SolicitudViajeSer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudViaje
        fields = '__all__'

#Solcitud Pago directo
class SolicitudPagoDirectoSer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudPagoDirecto
        fields = '__all__'
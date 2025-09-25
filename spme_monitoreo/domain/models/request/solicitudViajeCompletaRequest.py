# D:\proyecto_smpe\spme\spme_monitoreo\domain\models\request\solicitudViajeCompletaRequest.py
from rest_framework import serializers

class DetalleGastoSerializer(serializers.Serializer):
    partida = serializers.CharField(required=True)
    descripcion = serializers.CharField(required=True)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

class CrearSolicitudViajeCompletaRequest(serializers.Serializer):
    nombreEvento = serializers.CharField(required=True)
    fechaEvento = serializers.DateField(required=True)
    lugarRealizacion = serializers.CharField(required=True)
    entidadesParticipantes = serializers.CharField(required=True)
    entidadOrganizadora = serializers.CharField(required=True)
    entidadFinanciadora = serializers.CharField(required=True)
    fondoUnitas = serializers.BooleanField(required=True)
    solicitanteViaje = serializers.CharField(required=True)
    idSolicitanteDeViaje = serializers.IntegerField(required=True)
    justificacionAsistencia = serializers.CharField(required=True)
    tareasPrevias = serializers.CharField(required=True)
    DetalleGasto = DetalleGastoSerializer(many=True, required=True)
    montoTotal = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    formaPago = serializers.CharField(required=True)
    lugarDeSolicitud = serializers.CharField(required=True)
    fechaDeSolicitud = serializers.DateField(required=True)
    idresponsable = serializers.IntegerField(required=True)
    validacionResponsable = serializers.BooleanField(required=True)
    idcoordinador = serializers.IntegerField(required=True)
    validacionCoordinador = serializers.BooleanField(required=True)
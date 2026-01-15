from rest_framework import serializers
from spme_monitoreo.models import SolicitudViajeActPei

class SolicitudViajeActPeiSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudViajeActPei
        fields = [
            'id',
            'numeroFormulario',
            'evento',
            'lugarEvento',
            'institucionesParticipantes',
            'organizador',
            'quienCubreGastos',
            'justificacionAsistencia',
            'fondosUnitas',
            'tareasPrevias',
            'formaPago_id',
            'montoSolicitado',
            'lugarSolicitud',
            'fechaSolicitud',
            'fechaEvento',
            'detalleGasto',
            'validacionResponsable',
            'validacionCoordinador',
            'responsable_id',
            'coordinador_id',
            'usuario_id',
            'actividad_id',
            'tarea_id',
            'bloquearIconos',
            'datos_forma_pago'
        ]
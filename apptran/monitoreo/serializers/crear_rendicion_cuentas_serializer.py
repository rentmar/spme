# serializers.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import (RendicionCuentas, SolicitudReembolso, 
                                   SolicitudViaje, SolicitudPagoDirecto, SolicitudFondos)

class DetalleDestinoFondosSerializer(serializers.Serializer):
    factura_recibo = serializers.CharField(required=False, allow_blank=True, default="")
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    monto = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        default=0
    )

class RendicionCuentasCreateSerializer(serializers.ModelSerializer):
    detalleDestinoFondos = serializers.ListField(
        child=DetalleDestinoFondosSerializer(),
        required=False,
        allow_null=True,
        default=list
    )
    
    # Campos de relación con usuarios (referenciales)
    idadministrador = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        source='administrador',
        required=False,
        allow_null=True
    )
    idcontador = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        source='contador',
        required=False,
        allow_null=True
    )
    idcoordinador = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        source='coordinador',
        required=False,
        allow_null=True
    )
    idresponsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        source='responsable',
        required=False,
        allow_null=True
    )
    idusuarioLogeado = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), 
        source='usuario',
        required=False,
        allow_null=True
    )
    
    # Campos de actividad
    idActividad = serializers.PrimaryKeyRelatedField(
        queryset=Actividad.objects.all(), 
        source='actividad',
        required=False,
        allow_null=True
    )
    FechaActividad = serializers.DateField(
        source='fechaActividad', 
        required=False, 
        allow_null=True
    )
    
    # Campos de bloqueo
    bloquearIconoRC = serializers.BooleanField(
        source='bloquearIconos', 
        required=False, 
        default=True
    )
    
    # Campos de relación con solicitudes
    idSolicitudFondos = serializers.PrimaryKeyRelatedField(
        queryset=SolicitudFondos.objects.all(),
        source='solicitudFondos',
        required=False,
        allow_null=True
    )
    idSolicitudReembolso = serializers.PrimaryKeyRelatedField(
        queryset=SolicitudReembolso.objects.all(),
        source='solicitudReembolso',
        required=False,
        allow_null=True
    )
    idSolicitudViaje = serializers.PrimaryKeyRelatedField(
        queryset=SolicitudViaje.objects.all(),
        source='solicitudViaje',
        required=False,
        allow_null=True
    )
    idSolicitudPagoDirecto = serializers.PrimaryKeyRelatedField(
        queryset=SolicitudPagoDirecto.objects.all(),
        source='solicitudPagoDirecto',
        required=False,
        allow_null=True
    )
    idTarea = serializers.PrimaryKeyRelatedField(
        queryset=TareaActividad.objects.all(),
        source='tarea',
        required=False,
        allow_null=True
    )

    class Meta:
        model = RendicionCuentas
        fields = [
            # Campos básicos
            'numeroFormulario', 'cpteDiario', 'fechaDesembolso', 
            'montoDescargado', 'saldo', 'detalleDestinoFondos',
            
            # Validaciones
            'validacionResponsable', 'validacionCoordinador',
            'validacionContador', 'validacionAdministrador',
            
            # Usuarios (referenciales)
            'idadministrador', 'idcontador', 'idcoordinador', 
            'idresponsable', 'idusuarioLogeado',
            
            # Actividad
            'descripcionActividad', 'lugarActividad', 
            'FechaActividad', 'idActividad',
            
            # Bloqueo
            'bloquearIconoRC',
            
            # Relaciones con solicitudes
            'idSolicitudFondos', 'idSolicitudReembolso',
            'idSolicitudViaje', 'idSolicitudPagoDirecto',
            'idTarea'
        ]

    def validate_montoDescargado(self, value):
        """Validación para el monto descargado"""
        if value is None:
            raise serializers.ValidationError("El monto descargado es requerido")
        if value <= 0:
            raise serializers.ValidationError("El monto descargado debe ser mayor a 0")
        return value

    def validate_fechaDesembolso(self, value):
        """Permitir fechas nulas"""
        return value  # Acepta tanto fechas como null

    def create(self, validated_data):
        # Extraer datos relacionados
        detalle_destino_fondos = validated_data.pop('detalleDestinoFondos', [])
        
        # Crear la instancia de RendicionCuentas
        rendicion = RendicionCuentas.objects.create(**validated_data)
        
        # Asignar el detalle de destino de fondos si existe
        if detalle_destino_fondos:
            rendicion.detalleDestinoFondos = detalle_destino_fondos
            rendicion.save()
        
        return rendicion
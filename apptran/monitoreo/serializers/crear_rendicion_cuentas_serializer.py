# serializers.py
from rest_framework import serializers
from spme_autenticacion.models import Usuario
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import (RendicionCuentas, SolicitudReembolso, 
                                   SolicitudViaje, SolicitudPagoDirecto, SolicitudFondos)
from decimal import Decimal, InvalidOperation

class DetalleDestinoFondosSerializer(serializers.Serializer):
    fecha = serializers.CharField(
        required=False, 
        allow_blank=True, 
        default=None
    )
    
    partida = serializers.CharField(
        required=False, 
        allow_blank=True, 
        allow_null=True, 
        default=None
    )
    # fecha = serializers.DateField(required=False, allow_null=True, default=None)
    # partida = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    factura_recibo = serializers.CharField(required=False, allow_blank=True, default="")
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    monto = serializers.CharField(required=False, allow_null=True, default=0)
    def validate_monto(self, value):
        """Convierte el string a decimal si es necesario"""
        if value and isinstance(value, str):
            try:
                return str(Decimal(value))  # Convierte a string del decimal
            except (ValueError, InvalidOperation):
                raise serializers.ValidationError("Monto debe ser un número válido")
        return value

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
    fechaActividad = serializers.DateField(
        required=False, 
        allow_null=True
    )
    
    # Campos de bloqueo
    # bloquearIconoRC = serializers.BooleanField(
    #     source='bloquearIconos', 
    #     required=False, 
    #     default=True
    # )
    
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
            'montoDescargado', 'montoAsignado', 'saldo', 'detalleDestinoFondos',
            
            # Validaciones
            'validacionResponsable', 'validacionCoordinador',
            'validacionContador', 'validacionAdministrador',
            
            # Usuarios (referenciales)
            'idadministrador', 'idcontador', 'idcoordinador', 
            'idresponsable', 'idusuarioLogeado',
            
            # Actividad
            'descripcionActividad', 'lugarActividad', 
            'fechaActividad', 'idActividad', 'fechaRendicion',
            
            # Bloqueo
            # 'bloquearIconoRC',
            'bloquearIconos',
            
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

    def to_internal_value(self, data):
        """
        Convierte valores 0 a None para campos de usuarios
        Esto permite que el frontend envíe 0 en lugar de null
        """
        # Crear una copia mutable de los datos
        data_copy = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Lista de campos de usuario que pueden recibir 0 como null
        user_fields = [
            'idresponsable', 
            'idadministrador', 
            'idcontador', 
            'idcoordinador', 
            'idusuarioLogeado'
        ]
        
        # Convertir 0 a None para cada campo de usuario
        for field in user_fields:
            if field in data_copy and data_copy[field] == 0:
                data_copy[field] = None
        
        return super().to_internal_value(data_copy)

    def create(self, validated_data):
        # Extraer datos relacionados
        detalle_destino_fondos = validated_data.pop('detalleDestinoFondos', [])
        
        # Ignorar numeroFormulario si viene en los datos, ya que se autogenera
        validated_data.pop('numeroFormulario', None)

        # Crear la instancia de RendicionCuentas
        rendicion = RendicionCuentas.objects.create(**validated_data)
        
        # Generar número de formulario basado en el ID
        rendicion.numeroFormulario = f"FRC-{rendicion.id}"
        rendicion.save()

        # Asignar el detalle de destino de fondos si existe
        if detalle_destino_fondos:
            rendicion.detalleDestinoFondos = detalle_destino_fondos
            rendicion.save()
        
        return rendicion
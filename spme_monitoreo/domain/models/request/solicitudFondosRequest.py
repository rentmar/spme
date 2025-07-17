from rest_framework import serializers

class CrearSolicitudFondosRequest(serializers.Serializer):
    """
    Request para crear un Solicitud de Fondos.
    """
    nombre = serializers.CharField(max_length=50)
    paterno = serializers.CharField(max_length=50)
    materno = serializers.CharField(max_length=50)
    cargo = serializers.CharField(max_length=50)
    aprobador = serializers.CharField(max_length=50)
    descripcion = serializers.CharField(max_length=350)
    fecha_realizacion = serializers.DateField()
    objetivo_actividad = serializers.CharField(max_length=350)
    fuente_financiamiento = serializers.CharField(max_length=50)
    detalle_destino_fondos = serializers.CharField(max_length=350)
    beneficiario = serializers.CharField(max_length=50)
    documento_identidad_beneficiario = serializers.CharField(max_length=20)
    banco = serializers.CharField(max_length=50)
    numero_cuenta = serializers.CharField(max_length=40)
    tipo_cuenta = serializers.CharField(max_length=20)
    lugar_solicitud = serializers.CharField(max_length=50)
    fecha_solicitud = serializers.DateField()
    monto_solicitado = serializers.DecimalField(max_digits=10, decimal_places=2)
    responsable_aprobacion = serializers.BooleanField(default=False)
    responsable = serializers.IntegerField(required=True, allow_null=False)
    coordinador_aprobacion = serializers.BooleanField(default=False)
    coordinador = serializers.IntegerField(required=True, allow_null=False)

    def to_internal_value(self, data):
        """
        Convierte los campos a un formato interno.
        """
        internal_value = super().to_internal_value(data)
        return {
            'nombre': internal_value['nombre'],
            'paterno': internal_value['paterno'],
            'materno': internal_value['materno'],
            'cargo': internal_value['cargo'],
            'aprobador': internal_value['aprobador'],
            'descripcion': internal_value['descripcion'],
            'fechaRealizacion': internal_value['fecha_realizacion'],
            'objetivoActividad': internal_value['objetivo_actividad'],
            'fuenteFinanciamiento': internal_value['fuente_financiamiento'],
            'detalleDestinoFondos': internal_value['detalle_destino_fondos'],
            'beneficiario': internal_value['beneficiario'],
            'documentoIdentidadBeneficiario': internal_value['documento_identidad_beneficiario'],
            'banco': internal_value['banco'],
            'numeroCuenta': internal_value['numero_cuenta'],
            'tipoCuenta': internal_value['tipo_cuenta'],
            'lugarSolicitud': internal_value['lugar_solicitud'],
            'fechaSolicitud': internal_value['fecha_solicitud'],
            'montoSolicitado': internal_value['monto_solicitado'],
            'responsableAprobacion': internal_value['responsable_aprobacion'],
            'responsable': int(internal_value['responsable']),
            'coordinadorAprobacion': internal_value['coordinador_aprobacion'],
            'coordinador': int(internal_value['coordinador']),
        }
          
    
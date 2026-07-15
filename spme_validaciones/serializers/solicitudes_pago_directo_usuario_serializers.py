# spme/spme_validaciones/serializers/solicitudes_pago_directo_usuario_serializers.py
# serializers/solicitudes_pago_directo_usuario_serializers.py
from rest_framework import serializers


class TipoActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sigla = serializers.CharField(allow_null=True, allow_blank=True)
    tipo = serializers.CharField(allow_null=True, allow_blank=True)


class ResponsableActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField(allow_blank=True)


class ProyectoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True, allow_blank=True)
    nombre = serializers.CharField(allow_null=True, allow_blank=True)


class ActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True, allow_blank=True)
    nombre = serializers.CharField(allow_null=True, allow_blank=True)
    descripcion = serializers.CharField(allow_null=True, allow_blank=True)
    estado = serializers.CharField(allow_blank=True)
    estadoDisplay = serializers.CharField(allow_blank=True)
    tipo = TipoActividadSerializer(allow_null=True)
    fechaInicio = serializers.DateField(allow_null=True)
    fechaCierre = serializers.DateField(allow_null=True)
    presupuesto = serializers.FloatField(allow_null=True)
    responsable = ResponsableActividadSerializer(allow_null=True)
    proyecto = ProyectoSerializer(allow_null=True)


class TareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True, allow_blank=True)
    titulo = serializers.CharField(allow_null=True, allow_blank=True)
    descripcion = serializers.CharField(allow_null=True, allow_blank=True)
    estado = serializers.CharField(allow_blank=True)
    estadoDisplay = serializers.CharField(allow_blank=True)
    fechaEjecucion = serializers.DateField(allow_null=True)
    fechaLimite = serializers.DateField(allow_null=True)
    presupuesto = serializers.FloatField(allow_null=True)


class RevisorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField(allow_null=True, allow_blank=True)
    estado = serializers.CharField(allow_blank=True)
    fechaAsignacion = serializers.DateTimeField(allow_null=True)
    fechaResolucion = serializers.DateTimeField(allow_null=True)
    versionDocumento = serializers.CharField(allow_blank=True)
    comentarios = serializers.CharField(allow_blank=True)
    codigoSeguimiento = serializers.CharField(allow_blank=True)
    esRedactor = serializers.BooleanField()
    esUsuarioActual = serializers.BooleanField()


class UsuarioSolicitanteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField(allow_null=True, allow_blank=True)


class SolicitudPagoDirectoUsuarioSerializer(serializers.Serializer):
    # Identificación
    id = serializers.IntegerField()
    numeroForm = serializers.CharField(allow_null=True, allow_blank=True)
    tipoDocumento = serializers.CharField(allow_blank=True)
    subtipo = serializers.CharField(allow_blank=True)
    
    # Datos específicos de Pago Directo
    descripcionActividad = serializers.CharField(allow_blank=True)
    objetivoActividad = serializers.CharField(allow_blank=True)
    fechaRealizacionActividad = serializers.DateField(allow_null=True)
    
    # Actividad y Tarea
    actividad = ActividadSerializer(allow_null=True)
    tarea = TareaSerializer(allow_null=True)
    
    # Datos generales
    lugarSolicitud = serializers.CharField(allow_blank=True)
    fechaSolicitud = serializers.DateField(allow_null=True)
    montoSolicitado = serializers.FloatField()
    
    # Pertenencia y roles
    lePertenece = serializers.BooleanField()
    rolUsuario = serializers.CharField(allow_blank=True)
    esRedactor = serializers.BooleanField()
    esRevisor = serializers.BooleanField()
    pendienteRevision = serializers.BooleanField()
    
    # Estados
    estadoConsolidado = serializers.CharField(allow_blank=True)
    estadoMiValidacion = serializers.CharField(allow_null=True, allow_blank=True)
    
    # Versiones
    miVersionDocumento = serializers.CharField(allow_null=True, allow_blank=True)
    versionesComoRedactor = serializers.ListField(
        child=serializers.CharField(allow_blank=True)
    )
    
    # Estadísticas
    totalRevisores = serializers.IntegerField()
    revisoresQueAprobaron = serializers.IntegerField()
    revisoresQueRechazaron = serializers.IntegerField()
    revisoresPendientes = serializers.IntegerField()
    
    # Fechas
    fechaAsignacion = serializers.DateTimeField(allow_null=True)
    fechaResolucion = serializers.DateTimeField(allow_null=True)
    
    # Revisores
    revisores = RevisorSerializer(many=True)
    
    # Dueño
    usuarioSolicitante = UsuarioSolicitanteSerializer()
    
    # URLs
    url = serializers.CharField(allow_blank=True)
    urlAccion = serializers.CharField(allow_blank=True)


class ResumenSerializer(serializers.Serializer):
    totalSolicitudes = serializers.IntegerField()
    comoRedactor = serializers.IntegerField()
    comoRevisor = serializers.IntegerField()
    comoRedactorRevisor = serializers.IntegerField()
    pendientesRevision = serializers.IntegerField()
    aprobadas = serializers.IntegerField()
    rechazadas = serializers.IntegerField()
    sinRevision = serializers.IntegerField()


class SolicitudesPagoDirectoUsuarioResponseSerializer(serializers.Serializer):
    tipo = serializers.CharField(allow_blank=True)
    total = serializers.IntegerField()
    solicitudes = SolicitudPagoDirectoUsuarioSerializer(many=True)
    resumen = ResumenSerializer()
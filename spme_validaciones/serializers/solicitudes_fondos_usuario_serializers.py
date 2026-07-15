#spme/spme_validaciones/serializers/solicitudes_fondos_usuario_serializers.py
from rest_framework import serializers

class TipoActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sigla = serializers.CharField(allow_null=True)
    tipo = serializers.CharField(allow_null=True)

class ResponsableActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()

class ProyectoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True)
    nombre = serializers.CharField(allow_null=True)

class ActividadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True)
    nombre = serializers.CharField(allow_null=True)
    descripcion = serializers.CharField(allow_null=True, allow_blank=True)
    estado = serializers.CharField()
    estadoDisplay = serializers.CharField()
    tipo = TipoActividadSerializer(allow_null=True)
    fechaInicio = serializers.DateField(allow_null=True)
    fechaCierre = serializers.DateField(allow_null=True)
    presupuesto = serializers.FloatField(allow_null=True)
    responsable = ResponsableActividadSerializer(allow_null=True)
    proyecto = ProyectoSerializer(allow_null=True)

class TareaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    codigo = serializers.CharField(allow_null=True)
    titulo = serializers.CharField(allow_null=True)
    descripcion = serializers.CharField(allow_null=True,  allow_blank=True )
    estado = serializers.CharField()
    estadoDisplay = serializers.CharField()
    fechaEjecucion = serializers.DateField(allow_null=True)
    fechaLimite = serializers.DateField(allow_null=True)
    presupuesto = serializers.FloatField(allow_null=True)


class UsuarioSolicitanteSerializer(serializers.Serializer):
    """
    Serializer para información básica del dueño del formulario.
    """
    id = serializers.IntegerField(help_text="ID del usuario solicitante")
    nombre = serializers.CharField(
        allow_null=True,
        help_text="Nombre completo del usuario solicitante"
    )


class RevisorSerializer(serializers.Serializer):
    """Serializer para información detallada de cada revisor"""
    id = serializers.IntegerField(help_text="ID del revisor")
    nombre = serializers.CharField(
        allow_null=True,
        help_text="Nombre completo del revisor"
    )
    estado = serializers.CharField(
        help_text="Estado de su validación: PENDIENTE, APROBADO, RECHAZADO"
    )
    fechaAsignacion = serializers.DateTimeField(
        allow_null=True,
        help_text="Fecha cuando se le asignó la revisión"
    )
    fechaResolucion = serializers.DateTimeField(
        allow_null=True,
        help_text="Fecha cuando resolvió su revisión"
    )
    versionDocumento = serializers.CharField(
        help_text="Versión del documento que revisó"
    )
    comentarios = serializers.CharField(
        allow_blank=True,
        help_text="Observaciones o comentarios del revisor"
    )
    codigoSeguimiento = serializers.CharField(
        help_text="Código único de seguimiento de la validación"
    )
    esRedactor = serializers.BooleanField(
        help_text="True si este revisor también es redactor de la solicitud"
    )
    esUsuarioActual = serializers.BooleanField(
        help_text="True si este revisor es el usuario autenticado"
    )



class SolicitudFondosUsuarioSerializer(serializers.Serializer):
    """
    Serializer que representa UNA solicitud de fondos con su estado de validación.
    """
    # Identificación
    id = serializers.IntegerField(help_text="ID único de la solicitud")
    numeroForm = serializers.CharField(
        allow_null=True,
        help_text="Número de formulario asignado"
    )
    tipoDocumento = serializers.CharField(
        help_text="Tipo de documento (siempre 'Solicitud de Fondos')"
    )
    
    # Clasificación
    subtipo = serializers.CharField(
        help_text="Clasificación: 'Actividad' o 'Subactividad'"
    )

    #Actividad y tarea
    actividad = ActividadSerializer(allow_null=True)
    tarea = TareaSerializer(allow_null=True)

    
    # Datos de la solicitud
    lugarSolicitud = serializers.CharField(
        allow_null=True,
        help_text="Lugar donde se realiza la solicitud"
    )
    fechaSolicitud = serializers.DateField(
        allow_null=True,
        help_text="Fecha de la solicitud"
    )
    montoSolicitado = serializers.FloatField(
        help_text="Monto solicitado en la solicitud"
    )
    
    # Pertenencia y roles
    lePertenece = serializers.BooleanField(
        help_text="True si el usuario es el dueño del formulario"
    )
    rolUsuario = serializers.CharField(
        help_text="Rol del usuario: REDACTOR, REVISOR o REDACTOR_REVISOR"
    )
    esRedactor = serializers.BooleanField(
        help_text="True si el usuario es redactor en alguna validación"
    )
    esRevisor = serializers.BooleanField(
        help_text="True si el usuario es revisor en alguna validación"
    )
    pendienteRevision = serializers.BooleanField(
        help_text="True si el usuario tiene una revisión pendiente"
    )
    
    # Estados
    estadoConsolidado = serializers.CharField(
        help_text="Estado consolidado: Aprobado, Rechazado, Pendiente, Sin revisión"
    )
    estadoMiValidacion = serializers.CharField(
        allow_null=True,
        help_text="Estado de MI validación: PENDIENTE, APROBADO, RECHAZADO o null"
    )
    
    # Versiones de documento
    miVersionDocumento = serializers.CharField(
        allow_null=True,
        help_text="Versión del documento en mi validación como revisor"
    )
    versionesComoRedactor = serializers.ListField(
        child=serializers.CharField(),
        help_text="Versiones de documento donde soy redactor"
    )
    
    # Estadísticas de revisión
    totalRevisores = serializers.IntegerField(
        help_text="Número total de revisores asignados"
    )
    revisoresQueAprobaron = serializers.IntegerField(
        help_text="Cuántos revisores ya aprobaron"
    )
    revisoresQueRechazaron = serializers.IntegerField(
        help_text="Cuántos revisores rechazaron"
    )
    revisoresPendientes = serializers.IntegerField(
        help_text="Cuántos revisores aún no validan"
    )
    
    # Fechas de mi validación
    fechaAsignacion = serializers.DateTimeField(
        allow_null=True,
        help_text="Fecha cuando se me asignó la revisión"
    )
    fechaResolucion = serializers.DateTimeField(
        allow_null=True,
        help_text="Fecha cuando resolví mi revisión"
    )
    
    # Dueño del formulario
    usuarioSolicitante = UsuarioSolicitanteSerializer(
        help_text="Información del usuario dueño del formulario"
    )
    
    # URLs
    url = serializers.CharField(
        help_text="URL para ver/editar la solicitud"
    )
    urlAccion = serializers.CharField(
        help_text="Texto descriptivo de la acción"
    )
    #lista de revisores
    revisores = RevisorSerializer(
        many=True,
        help_text="Información detallada de cada revisor asignado"
    )


class ResumenSerializer(serializers.Serializer):
    """Serializer para el resumen estadístico"""
    totalSolicitudes = serializers.IntegerField()
    comoRedactor = serializers.IntegerField()
    comoRevisor = serializers.IntegerField()
    comoRedactorRevisor = serializers.IntegerField()
    pendientesRevision = serializers.IntegerField()
    aprobadas = serializers.IntegerField()
    rechazadas = serializers.IntegerField()
    sinRevision = serializers.IntegerField()


class SolicitudesFondosUsuarioResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta completa del endpoint.
    """
    tipo = serializers.CharField(
        help_text="Tipo de solicitudes en esta respuesta: 'solicitudes_fondos'"
    )
    total = serializers.IntegerField(
        help_text="Total de solicitudes encontradas"
    )
    solicitudes = SolicitudFondosUsuarioSerializer(
        many=True,
        help_text="Lista de solicitudes de fondos"
    )
    resumen = ResumenSerializer(
        help_text="Resumen estadístico de las solicitudes"
    )
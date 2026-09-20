# spme/spme_validaciones/serializers/permisos_documento_serializers.py
from rest_framework import serializers


class RedactorSerializer(serializers.Serializer):
    """
    Serializa al redactor del documento (documento.usuario).
    """
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    paterno = serializers.CharField()
    materno = serializers.CharField()
    correo = serializers.CharField(allow_blank=True)
    cargo = serializers.CharField(allow_blank=True)
    username = serializers.CharField()


class RevisorSerializer(serializers.Serializer):
    """
    Serializa una instancia de Validacion* como revisor.

    El `rol` es siempre 'revisor'. El rol contextual (redactor vs revisor)
    se determina por los registros, no por el usuario.
    """
    rol = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='usuarioValidador.id')
    nombre = serializers.CharField(source='usuarioValidador.nombre')
    paterno = serializers.CharField(source='usuarioValidador.paterno')
    materno = serializers.CharField(source='usuarioValidador.materno')
    correo = serializers.CharField(source='usuarioValidador.correo', allow_blank=True)
    username = serializers.CharField(source='usuarioValidador.username')
    voto = serializers.SerializerMethodField()
    estado = serializers.CharField()
    fechaVoto = serializers.DateTimeField(source='fechaResolucion', allow_null=True)
    fechaAsignacion = serializers.DateTimeField(allow_null=True)

    def get_rol(self, obj) -> str:
        return 'revisor'

    def get_voto(self, obj) -> bool:
        return obj.estado == 'APROBADO'


class PermisosDocumentoSerializer(serializers.Serializer):
    """
    Serializer de salida del endpoint /documentos/<tipo>/<id>/permisos.

    Recibe un dict:
        {
            'documento': instancia,
            'permisos': PermisosDocumento,
            'validaciones': queryset,
        }
    """
    estadoDocumento = serializers.CharField(source='permisos.estado_documento')
    redactor = serializers.SerializerMethodField()
    revisores = serializers.SerializerMethodField()
    puedeEditar = serializers.BooleanField(source='permisos.puede_editar')
    motivoBloqueo = serializers.CharField(source='permisos.motivo_bloqueo', allow_null=True)
    esRedactor = serializers.BooleanField(source='permisos.es_redactor')
    puedeSolicitarModificacion = serializers.BooleanField(source='permisos.puede_solicitar_modificacion')
    peticionesModificacion = serializers.SerializerMethodField()

    def get_redactor(self, obj):
        redactor = obj['documento'].usuario
        if not redactor:
            return None
        return RedactorSerializer(redactor).data

    def get_revisores(self, obj):
        return RevisorSerializer(obj['validaciones'], many=True).data

    def get_peticionesModificacion(self, obj):
        # TODO: cuando exista PeticionModificacion, serializar la lista.
        # El contrato ya expone [] para que el frontend no cambie.
        return []
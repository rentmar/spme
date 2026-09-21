# spme/spme_validaciones/serializers/peticiones/peticion_serializers.py
from rest_framework import serializers

from spme_validaciones.models_peticiones import (
    PeticionModificacion,
    TipoPeticionModificacion,
)


class SolicitanteMinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    nombre = serializers.CharField()


class PeticionModificacionSerializer(serializers.ModelSerializer):
    """
    Contrato acordado con el frontend:
    {
      "id": 123,
      "tipo": "EDICION_TOTAL",
      "tipoNombre": "Edición total",
      "estado": "INICIADA",
      "justificativo": "...",
      "solicitante": { "id": 72, "username": "arecoba", "nombre": "Alvaro" },
      "fechaInicio": "...",
      "fechaResolucion": null,
      "motivoAnulacion": null
    }
    """
    tipo = serializers.CharField(source='tipo.codigo')
    tipoNombre = serializers.CharField(source='tipo.nombre')
    solicitante = serializers.SerializerMethodField()
    fechaInicio = serializers.DateTimeField(source='fecha_inicio')
    fechaResolucion = serializers.DateTimeField(source='fecha_resolucion', allow_null=True)
    motivoAnulacion = serializers.CharField(source='motivo_anulacion', allow_null=True)

    class Meta:
        model = PeticionModificacion
        fields = [
            'id',
            'tipo',
            'tipoNombre',
            'estado',
            'justificativo',
            'solicitante',
            'fechaInicio',
            'fechaResolucion',
            'motivoAnulacion',
        ]

    def get_solicitante(self, obj):
        u = obj.solicitante
        if not u:
            return None
        return {
            'id': u.id,
            'username': u.username,
            'nombre': u.nombre,
        }


class PeticionCrearSerializer(serializers.Serializer):
    """
    Entrada para crear una petición de modificación.

    El frontend envía:
      - tipo: codigo del tipo (ej. "EDICION_TOTAL")
      - content_type: "app_label.model" del objetivo
      - object_id: id del documento objetivo
      - justificativo: texto
      - payload: dict (opcional, según tipo)
    """
    tipo = serializers.CharField()
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()
    justificativo = serializers.CharField()
    payload = serializers.JSONField(required=False, default=dict)


class TipoPeticionModificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPeticionModificacion
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'activo',
            'esquema_payload',
            'content_types_permitidos',
            'requiere_versionado',
            'orden',
        ]
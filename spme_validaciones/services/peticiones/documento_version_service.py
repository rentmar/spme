# spme_validaciones/services/peticiones/documento_version_service.py
# spme_validaciones/services/peticiones/documento_version_service.py

import datetime
import uuid
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms.models import model_to_dict

from spme_validaciones.models_peticiones import DocumentoVersion


class DocumentoVersionService:
    """
    Servicio para crear y consultar snapshots de documentos.

    Un snapshot guarda el contenido completo del documento al momento de
    ejecutarse una petición de tipo EDICION_TOTAL (o cualquier otra que
    tenga requiere_versionado=True).
    """

    # Campos que NUNCA van al snapshot, en cualquier modelo.
    CAMPOS_EXCLUIDOS = {
        'id',
        'timestamp_registro',
        'timestamp_ultima_modificacion',
    }

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------
    def crear_snapshot(self, documento, peticion, aprobado_por):
        """
        Crea un DocumentoVersion con el contenido íntegro del documento.

        Args:
            documento: instancia del modelo objetivo (SolicitudFondos, etc.).
            peticion: PeticionModificacion que origina el snapshot.
            aprobado_por: instancia de Usuario que aprueba.

        Returns:
            DocumentoVersion creada.
        """
        content_type = ContentType.objects.get_for_model(documento)
        numero_version = self._siguiente_numero_version(
            content_type=content_type,
            object_id=documento.pk,
        )

        contenido = self._serializar_documento(documento)

        with transaction.atomic():
            version = DocumentoVersion.objects.create(
                documento_content_type=content_type,
                documento_object_id=documento.pk,
                numero_version=numero_version,
                contenido_snapshot=contenido,
                peticion_origen=peticion,
                aprobado_por=aprobado_por,
            )
        return version

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def obtener_versiones(self, documento):
        """Devuelve todas las versiones de un documento, ordenadas desc."""
        content_type = ContentType.objects.get_for_model(documento)
        return DocumentoVersion.objects.filter(
            documento_content_type=content_type,
            documento_object_id=documento.pk,
        ).order_by('-numero_version')

    def obtener_ultima_version(self, documento):
        """Devuelve la última versión del documento, o None."""
        return self.obtener_versiones(documento).first()

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _siguiente_numero_version(self, content_type, object_id):
        """
        Calcula el número de versión siguiente para un documento.
        Si no hay versiones previas, devuelve 1.
        """
        ultima = (
            DocumentoVersion.objects
            .filter(
                documento_content_type=content_type,
                documento_object_id=object_id,
            )
            .order_by('-numero_version')
            .first()
        )
        return (ultima.numero_version + 1) if ultima else 1

    def _serializar_documento(self, documento):
        """
        Serializa el documento a un dict apto para JSONField.

        Usa model_to_dict, excluye CAMPOS_EXCLUIDOS, y aplica una
        normalización recursiva que convierte tipos no nativos de JSON
        (date, datetime, Decimal, UUID, etc.) a string.
        """
        data = model_to_dict(documento)
        for campo in self.CAMPOS_EXCLUIDOS:
            data.pop(campo, None)
        return self._normalizar_json(data)

    def _normalizar_json(self, valor):
        """
        Convierte recursivamente tipos no serializables por JSON.
        - date/datetime -> ISO string
        - Decimal -> string
        - UUID -> string
        - dict/list -> recursión
        """
        if valor is None or isinstance(valor, (bool, int, float, str)):
            return valor

        if isinstance(valor, (datetime.date, datetime.datetime)):
            return valor.isoformat()

        if isinstance(valor, Decimal):
            return str(valor)

        if isinstance(valor, uuid.UUID):
            return str(valor)

        if isinstance(valor, dict):
            return {k: self._normalizar_json(v) for k, v in valor.items()}

        if isinstance(valor, (list, tuple)):
            return [self._normalizar_json(v) for v in valor]

        # Fallback: convertir a string
        return str(valor)
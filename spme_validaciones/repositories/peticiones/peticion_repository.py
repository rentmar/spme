# spme/spme_validaciones/repositories/peticiones/peticion_repository.py
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from spme_validaciones.models_peticiones import (
    PeticionModificacion,
    TipoPeticionModificacion,
)
from spme_validaciones.constants_peticiones import (
    ESTADO_INICIADA,
    ESTADO_RESUELTA_EJECUTADA,
    ESTADO_RESUELTA_ANULADA,
)


class PeticionRepository:
    """
    Acceso a datos de PeticionModificacion.
    No contiene lógica de negocio, solo consultas.
    """

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def obtener_por_id(self, peticion_id):
        return (
            PeticionModificacion.objects
            .select_related('tipo', 'solicitante', 'resuelto_por', 'objetivo_content_type')
            .filter(pk=peticion_id)
            .first()
        )

    def obtener_iniciada_por_objetivo(self, content_type, object_id):
        return (
            PeticionModificacion.objects
            .filter(
                objetivo_content_type=content_type,
                objetivo_object_id=object_id,
                estado=ESTADO_INICIADA,
            )
            .first()
        )

    def listar_por_objetivo(self, content_type, object_id):
        return (
            PeticionModificacion.objects
            .select_related('tipo', 'solicitante', 'resuelto_por')
            .filter(
                objetivo_content_type=content_type,
                objetivo_object_id=object_id,
            )
            .order_by('-fecha_inicio')
        )

    def listar_por_solicitante(self, usuario):
        return (
            PeticionModificacion.objects
            .select_related('tipo', 'objetivo_content_type')
            .filter(solicitante=usuario)
            .order_by('-fecha_inicio')
        )

    def tiene_peticion_abierta(self, content_type, object_id):
        return PeticionModificacion.objects.filter(
            objetivo_content_type=content_type,
            objetivo_object_id=object_id,
            estado=ESTADO_INICIADA,
        ).exists()

    def tiene_edicion_total_ejecutada_no_consumida(self, content_type, object_id):
        return PeticionModificacion.objects.filter(
            objetivo_content_type=content_type,
            objetivo_object_id=object_id,
            estado=ESTADO_RESUELTA_EJECUTADA,
            tipo__codigo='EDICION_TOTAL',
            fecha_consumo__isnull=True,
        ).exists()

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def crear(self, **kwargs):
        return PeticionModificacion.objects.create(**kwargs)

    def guardar(self, peticion, update_fields=None):
        peticion.save(update_fields=update_fields)
        return peticion


class TipoPeticionRepository:
    """
    Acceso a datos del catálogo TipoPeticionModificacion.
    """

    def obtener_por_codigo(self, codigo):
        return TipoPeticionModificacion.objects.filter(codigo=codigo).first()

    def obtener_activo_por_codigo(self, codigo):
        return TipoPeticionModificacion.objects.filter(codigo=codigo, activo=True).first()

    def listar_activos(self):
        return TipoPeticionModificacion.objects.filter(activo=True).order_by('orden', 'codigo')

    def listar_todos(self):
        return TipoPeticionModificacion.objects.all().order_by('orden', 'codigo')

    def crear(self, **kwargs):
        return TipoPeticionModificacion.objects.create(**kwargs)
# spme_validaciones/services/peticiones/peticion_service.py

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone

from spme_validaciones.constants_peticiones import (
    CARGO_ADMIN,
    ESTADO_INICIADA,
    ESTADO_RESUELTA_ANULADA,
    ESTADO_RESUELTA_EJECUTADA,
    TIPO_EDICION_TOTAL,
)
from spme_validaciones.models_peticiones import PeticionModificacion
from spme_validaciones.repositories.peticiones.peticion_repository import (
    PeticionRepository, TipoPeticionRepository,
)
from spme_validaciones.services.peticiones.handlers import registry


class PeticionService:
    """
    Lógica de negocio del sistema de peticiones de modificación.
    """

    def __init__(self):
        self.repo = PeticionRepository()
        self.repo_tipo = TipoPeticionRepository()

    # ==================================================================
    # Autorización
    # ==================================================================
    @staticmethod
    def es_admin(usuario):
        return getattr(usuario, 'cargo', None) == CARGO_ADMIN

    @classmethod
    def puede_iniciar(cls, documento, usuario):
        """
        Pueden iniciar peticiones sobre un documento:
          - El redactor (documento.usuario_id == usuario.id)
          - Un admin (cargo == 'admin')
        """
        if cls.es_admin(usuario):
            return True
        return documento.usuario_id == usuario.id

    # ==================================================================
    # Crear
    # ==================================================================
    def crear_peticion(self, *, tipo_codigo, content_type_str, object_id,
                       solicitante, justificativo, payload=None):
        """
        Crea una petición de modificación.

        Valida:
          - tipo existe y está activo
          - content_type del objetivo está permitido para ese tipo
          - objetivo existe
          - solicitante tiene permiso (redactor o admin)
          - no hay otra petición INICIADA sobre el mismo objetivo
          - si es EDICION_TOTAL: no hay otra ejecutada no consumida
        """
        payload = payload or {}

        # 1. Tipo
        tipo = self.repo_tipo.obtener_activo_por_codigo(tipo_codigo)
        if not tipo:
            raise ValidationError(f"Tipo '{tipo_codigo}' no existe o está inactivo.")

        # 2. ContentType
        try:
            app_label, model = content_type_str.split('.')
        except ValueError:
            raise ValidationError(f"content_type inválido: '{content_type_str}'")
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            raise ValidationError(f"ContentType no existe: '{content_type_str}'")

        if content_type_str not in (tipo.content_types_permitidos or []):
            raise ValidationError(
                f"El tipo '{tipo.codigo}' no permite objetivos de tipo '{content_type_str}'."
            )

        # 3. Objetivo
        modelo = content_type.model_class()
        documento = modelo.objects.filter(pk=object_id).first()
        if not documento:
            raise ValidationError(
                f"El documento objetivo no existe ({content_type_str}#{object_id})."
            )

        # 4. Permiso
        if not self.puede_iniciar(documento, solicitante):
            raise PermissionDenied(
                "No tienes permiso para iniciar peticiones sobre este documento."
            )

        # 5. No debe haber otra INICIADA sobre el objetivo
        if self.repo.tiene_peticion_abierta(content_type, object_id):
            raise ValidationError(
                "Ya existe una petición INICIADA sobre este documento."
            )

        # 6. Regla B para EDICION_TOTAL: no acumular ejecutadas no consumidas
        if tipo.codigo == TIPO_EDICION_TOTAL:
            if self.repo.tiene_edicion_total_ejecutada_no_consumida(content_type, object_id):
                raise ValidationError(
                    "Ya hay una edición total autorizada y no consumida sobre este documento. "
                    "Debes guardar los cambios antes de solicitar otra."
                )

        # 7. Crear
        peticion = self.repo.crear(
            tipo=tipo,
            objetivo_content_type=content_type,
            objetivo_object_id=object_id,
            solicitante=solicitante,
            justificativo=justificativo,
            payload=payload,
        )
        return peticion

    # ==================================================================
    # Ejecutar
    # ==================================================================
    def ejecutar(self, peticion, usuario):
        """
        Ejecuta una petición: corre el handler y pasa a RESUELTA_EJECUTADA.
        """
        if peticion.estado != ESTADO_INICIADA:
            raise ValidationError(
                f"La petición no está INICIADA (estado: {peticion.estado})."
            )

        if not (peticion.solicitante_id == usuario.id or self.es_admin(usuario)):
            raise PermissionDenied(
                "Solo el solicitante o un admin pueden ejecutar la petición."
            )

        handler = registry.obtener_handler(peticion.tipo.codigo)
        if not handler:
            raise ValidationError(
                f"No hay handler registrado para '{peticion.tipo.codigo}'."
            )

        documento = peticion.objetivo
        if documento is None:
            raise ValidationError("El documento objetivo ya no existe.")

        with transaction.atomic():
            handler(peticion, documento)

            peticion.estado = ESTADO_RESUELTA_EJECUTADA
            peticion.fecha_resolucion = timezone.now()
            peticion.resuelto_por = usuario
            self.repo.guardar(
                peticion,
                update_fields=['estado', 'fecha_resolucion', 'resuelto_por'],
            )
        return peticion

    # ==================================================================
    # Anular
    # ==================================================================
    def anular(self, peticion, usuario, motivo):
        """
        Anula una petición INICIADA. No aplica ningún efecto.
        """
        if peticion.estado != ESTADO_INICIADA:
            raise ValidationError(
                f"La petición no está INICIADA (estado: {peticion.estado})."
            )

        if not (peticion.solicitante_id == usuario.id or self.es_admin(usuario)):
            raise PermissionDenied(
                "Solo el solicitante o un admin pueden anular la petición."
            )

        if not motivo or not motivo.strip():
            raise ValidationError("El motivo de anulación es obligatorio.")

        peticion.estado = ESTADO_RESUELTA_ANULADA
        peticion.fecha_resolucion = timezone.now()
        peticion.motivo_anulacion = motivo
        peticion.resuelto_por = usuario
        self.repo.guardar(
            peticion,
            update_fields=['estado', 'fecha_resolucion', 'motivo_anulacion', 'resuelto_por'],
        )
        return peticion

    # ==================================================================
    # Consumir (para EDICION_TOTAL)
    # ==================================================================
    def marcar_consumida(self, peticion):
        """
        Marca la petición como consumida. Se llama desde el endpoint de
        guardado del documento cuando se aplica la edición autorizada.
        """
        if peticion.fecha_consumo is not None:
            return peticion
        peticion.fecha_consumo = timezone.now()
        self.repo.guardar(peticion, update_fields=['fecha_consumo'])
        return peticion

    def obtener_edicion_total_no_consumida(self, documento):
        """
        Devuelve la EDICION_TOTAL ejecutada no consumida para un documento,
        o None. Útil para el endpoint de guardado.
        """
        content_type = ContentType.objects.get_for_model(documento)
        return (
            PeticionModificacion.objects
            .filter(
                objetivo_content_type=content_type,
                objetivo_object_id=documento.pk,
                estado=ESTADO_RESUELTA_EJECUTADA,
                tipo__codigo=TIPO_EDICION_TOTAL,
                fecha_consumo__isnull=True,
            )
            .order_by('-fecha_resolucion')
            .first()
        )

    # ==================================================================
    # Consultas (para hooks de permisos)
    # ==================================================================
    def tiene_peticion_abierta(self, documento):
        content_type = ContentType.objects.get_for_model(documento)
        return self.repo.tiene_peticion_abierta(content_type, documento.pk)

    def puede_solicitar_modificacion(self, documento, usuario):
        """Regla simple: redactor o admin."""
        return self.puede_iniciar(documento, usuario)

    def listar_por_documento(self, documento):
        content_type = ContentType.objects.get_for_model(documento)
        return self.repo.listar_por_objetivo(content_type, documento.pk)
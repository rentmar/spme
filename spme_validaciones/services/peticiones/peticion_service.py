# spme_validaciones/services/peticiones/peticion_service.py
# spme_validaciones/services/peticiones/peticion_service.py

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone

from spme_validaciones.constants import TIPOS_DOCUMENTO
from spme_validaciones.constants_peticiones import (
    CARGO_ADMIN,
    ESTADO_INICIADA,
    ESTADO_RESUELTA_ANULADA,
    ESTADO_RESUELTA_EJECUTADA,
    TIPO_EDICION_TOTAL,
)
from spme_validaciones.models_peticiones import PeticionModificacion
from spme_validaciones.repositories.peticiones.peticion_repository import (
    PeticionRepository,
    TipoPeticionRepository,
)
from spme_validaciones.services.peticiones.handlers import registry

from spme_validaciones.services.peticiones.documento_version_service import (
    DocumentoVersionService
)


class PeticionService:
    """
    Lógica de negocio del sistema de peticiones de modificación.
    """

    def __init__(self):
        self.repo = PeticionRepository()
        self.repo_tipo = TipoPeticionRepository()
        self.version_service = DocumentoVersionService()

    # ==================================================================
    # Autorización
    # ==================================================================

    @staticmethod
    def es_admin(usuario):
        """
        Un administrador puede iniciar peticiones sobre cualquier
        documento.
        """
        return (
            usuario is not None
            and getattr(usuario, "cargo", "").strip().lower() == CARGO_ADMIN
        )


    @classmethod
    def puede_iniciar(cls, documento, usuario):
        """
        Puede iniciar una petición de modificación:

        1. Administrador.
        2. Dueño/redactor del documento.
        """

        if not usuario:
            return False

        # Admin puede modificar cualquier documento
        if cls.es_admin(usuario):
            return True

        # El redactor/dueño puede modificar su propio documento
        return documento.usuario_id == usuario.id
    # ==================================================================
    # Resolver documento
    # ==================================================================

    @staticmethod
    def obtener_config_documento(documento_tipo):
        """
        Obtiene la configuración del documento a partir del identificador
        funcional utilizado por el API.

        Ejemplo:
            'solicitud-fondos'
            'solicitud-viaje'
            'rendicion-cuentas'
        """
        config = TIPOS_DOCUMENTO.get(documento_tipo)

        if not config:
            raise ValidationError(
                f"Tipo de documento inválido: '{documento_tipo}'."
            )

        return config

    @classmethod
    def obtener_documento(cls, documento_tipo, documento_id):
        """
        Obtiene el documento real a partir de:

            documento_tipo = 'solicitud-fondos'
            documento_id = 36
        """
        config = cls.obtener_config_documento(documento_tipo)

        modelo = config['modelo']

        documento = modelo.objects.filter(pk=documento_id).first()

        if not documento:
            raise ValidationError(
                f"El documento no existe "
                f"({documento_tipo}#{documento_id})."
            )

        return documento

    # ==================================================================
    # Crear
    # ==================================================================

    def crear_peticion(
        self,
        *,
        tipo_codigo,
        documento_tipo,
        documento_id,
        solicitante,
        justificativo,
        payload=None,
    ):
        """
        Crea una petición de modificación.

        Valida:
          - tipo existe y está activo
          - tipo de documento permitido para ese tipo de petición
          - documento existe
          - solicitante tiene permiso
          - no hay otra petición INICIADA sobre el documento
          - si es EDICION_TOTAL:
                no hay otra ejecutada no consumida
        """

        payload = payload or {}

        # --------------------------------------------------------------
        # 1. Tipo de petición
        # --------------------------------------------------------------

        tipo = self.repo_tipo.obtener_activo_por_codigo(tipo_codigo)

        if not tipo:
            raise ValidationError(
                f"Tipo '{tipo_codigo}' no existe o está inactivo."
            )

        # --------------------------------------------------------------
        # 2. Tipo de documento
        # --------------------------------------------------------------

        config = self.obtener_config_documento(documento_tipo)

        if documento_tipo not in (tipo.content_types_permitidos or []):
            raise ValidationError(
                f"El tipo '{tipo.codigo}' no permite documentos "
                f"de tipo '{documento_tipo}'."
            )

        # --------------------------------------------------------------
        # 3. Obtener documento
        # --------------------------------------------------------------

        modelo = config['modelo']

        documento = modelo.objects.filter(pk=documento_id).first()

        if not documento:
            raise ValidationError(
                f"El documento no existe "
                f"({documento_tipo}#{documento_id})."
            )

        # --------------------------------------------------------------
        # 4. ContentType interno
        # --------------------------------------------------------------

        content_type = ContentType.objects.get_for_model(documento)

        # --------------------------------------------------------------
        # 5. Permiso para iniciar petición
        # --------------------------------------------------------------

        if not self.puede_iniciar(documento, solicitante):
            raise PermissionDenied(
                "No tienes permiso para iniciar peticiones "
                "sobre este documento."
            )

        # --------------------------------------------------------------
        # 6. No debe existir otra petición INICIADA
        # --------------------------------------------------------------

        if self.repo.tiene_peticion_abierta(
            content_type,
            documento_id,
        ):
            raise ValidationError(
                "Ya existe una petición INICIADA "
                "sobre este documento."
            )

        # --------------------------------------------------------------
        # 7. Regla EDICION_TOTAL
        # --------------------------------------------------------------

        if tipo.codigo == TIPO_EDICION_TOTAL:

            if self.repo.tiene_edicion_total_ejecutada_no_consumida(
                content_type,
                documento_id,
            ):
                raise ValidationError(
                    "Ya hay una edición total autorizada y no consumida "
                    "sobre este documento. Debes guardar los cambios "
                    "antes de solicitar otra."
                )

        # --------------------------------------------------------------
        # 8. Crear petición
        # --------------------------------------------------------------

        # peticion = self.repo.crear(
        #     tipo=tipo,
        #     objetivo_content_type=content_type,
        #     objetivo_object_id=documento_id,
        #     solicitante=solicitante,
        #     justificativo=justificativo,
        #     payload=payload,
        # )

        # return peticion
        with transaction.atomic():

            peticion = self.repo.crear(
                tipo=tipo,
                objetivo_content_type=content_type,
                objetivo_object_id=documento_id,
                solicitante=solicitante,
                justificativo=justificativo,
                payload=payload,
            )

            if tipo.requiere_versionado:
                self.version_service.crear_snapshot(
                    documento=documento,
                    peticion=peticion,
                    aprobado_por=solicitante,
                )

        return peticion

    # ==================================================================
    # Ejecutar
    # ==================================================================

    def ejecutar(self, peticion, usuario):
        """
        Ejecuta una petición:

            INICIADA
                ↓
            handler
                ↓
            RESUELTA_EJECUTADA
        """

        if peticion.estado != ESTADO_INICIADA:
            raise ValidationError(
                f"La petición no está INICIADA "
                f"(estado: {peticion.estado})."
            )

        if not (
            peticion.solicitante_id == usuario.id
            or self.es_admin(usuario)
        ):
            raise PermissionDenied(
                "Solo el solicitante o un admin pueden ejecutar "
                "la petición."
            )

        handler = registry.obtener_handler(
            peticion.tipo.codigo
        )

        if not handler:
            raise ValidationError(
                f"No hay handler registrado para "
                f"'{peticion.tipo.codigo}'."
            )

        documento = peticion.objetivo

        if documento is None:
            raise ValidationError(
                "El documento objetivo ya no existe."
            )

        with transaction.atomic():

            handler(peticion, documento)

            ahora = timezone.now()

            peticion.estado = ESTADO_RESUELTA_EJECUTADA
            peticion.fecha_resolucion = ahora
            peticion.resuelto_por = usuario
            peticion.fecha_consumo = ahora

            self.repo.guardar(
                peticion,
                update_fields=[
                    'estado',
                    'fecha_resolucion',
                    'resuelto_por',
                    'fecha_consumo',
                ],
            )

        return peticion

    # ==================================================================
    # Anular
    # ==================================================================

    def anular(self, peticion, usuario, motivo):
        """
        Anula una petición INICIADA.
        No aplica ningún efecto sobre el documento.
        """

        if peticion.estado != ESTADO_INICIADA:
            raise ValidationError(
                f"La petición no está INICIADA "
                f"(estado: {peticion.estado})."
            )

        if not (
            peticion.solicitante_id == usuario.id
            or self.es_admin(usuario)
        ):
            raise PermissionDenied(
                "Solo el solicitante o un admin pueden "
                "anular la petición."
            )

        if not motivo or not motivo.strip():
            raise ValidationError(
                "El motivo de anulación es obligatorio."
            )

        peticion.estado = ESTADO_RESUELTA_ANULADA
        peticion.fecha_resolucion = timezone.now()
        peticion.motivo_anulacion = motivo
        peticion.resuelto_por = usuario

        self.repo.guardar(
            peticion,
            update_fields=[
                'estado',
                'fecha_resolucion',
                'motivo_anulacion',
                'resuelto_por',
            ],
        )

        return peticion

    # ==================================================================
    # Consumir autorización
    # ==================================================================

    def marcar_consumida(self, peticion):
        """
        Marca una petición ejecutada como consumida.

        Se utiliza principalmente para EDICION_TOTAL cuando el
        documento finalmente guarda los cambios autorizados.
        """

        if peticion.fecha_consumo is not None:
            return peticion

        peticion.fecha_consumo = timezone.now()

        self.repo.guardar(
            peticion,
            update_fields=['fecha_consumo'],
        )

        return peticion

    # ==================================================================
    # Obtener EDICION_TOTAL disponible
    # ==================================================================

    def obtener_edicion_total_no_consumida(self, documento):
        """
        Devuelve la EDICION_TOTAL ejecutada y todavía no consumida
        para el documento.

        Devuelve:
            PeticionModificacion
            o None
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
    # Consultas
    # ==================================================================

    def tiene_peticion_abierta(self, documento):
        """
        Indica si el documento tiene una petición INICIADA.
        """

        content_type = ContentType.objects.get_for_model(documento)

        return self.repo.tiene_peticion_abierta(
            content_type,
            documento.pk,
        )

    def puede_solicitar_modificacion(self, documento, usuario):
        """
        Regla simple:
            redactor o admin.
        """

        return self.puede_iniciar(
            documento,
            usuario,
        )

    def listar_por_documento(self, documento):
        """
        Lista todas las peticiones asociadas al documento.
        """

        content_type = ContentType.objects.get_for_model(documento)

        return self.repo.listar_por_objetivo(
            content_type,
            documento.pk,
        )
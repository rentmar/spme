# repositories/referencias/referencia_repository.py
import logging
from typing import List, Optional
from django.contrib.contenttypes.models import ContentType
from spme_repositorio.models import ReferenciaExterna

logger = logging.getLogger(__name__)


class ReferenciaRepository:
    """Acceso a datos para ReferenciaExterna."""

    def crear(self, url, nombre, categoria, content_object, creado_por, descripcion='', orden=0):
        referencia = ReferenciaExterna.objects.create(
            url=url, nombre=nombre, categoria=categoria,
            content_object=content_object, descripcion=descripcion,
            orden=orden, creado_por=creado_por,
        )
        logger.info(f"Referencia creada: {referencia.id}")
        return referencia

    def obtener_por_id(self, referencia_id) -> Optional[ReferenciaExterna]:
        return ReferenciaExterna.objects.filter(pk=referencia_id).first()

    def listar_por_objeto(self, content_object) -> List[ReferenciaExterna]:
        ct = ContentType.objects.get_for_model(content_object)
        return list(
            ReferenciaExterna.objects.filter(
                content_type=ct, object_id=content_object.pk,
            ).order_by('orden', '-creado_en')
        )

    def eliminar(self, referencia):
        ref_id = referencia.id
        referencia.delete()
        logger.info(f"Referencia eliminada: {ref_id}")
# services/referencias/referencia_service.py
import logging
from typing import List
from django.db import transaction
from spme_repositorio.repositories.referencias.referencia_repository import ReferenciaRepository

logger = logging.getLogger(__name__)


class ReferenciaService:

    def __init__(self):
        self._repo = ReferenciaRepository()

    @transaction.atomic
    def crear(self, url, nombre, content_object, creado_por, categoria='OTRO', descripcion='', orden=0):
        return self._repo.crear(url=url, nombre=nombre, categoria=categoria, content_object=content_object, creado_por=creado_por, descripcion=descripcion, orden=orden)

    @transaction.atomic
    def crear_bulk(self, referencias_data, content_object, creado_por):
        creadas = []
        for ref in referencias_data:
            r = self._repo.crear(url=ref['url'], nombre=ref.get('nombre', ref['url'][:100]), categoria=ref.get('categoria', 'OTRO'), content_object=content_object, creado_por=creado_por, descripcion=ref.get('descripcion', ''), orden=ref.get('orden', 0))
            creadas.append(r)
        return creadas

    def eliminar(self, referencia):
        self._repo.eliminar(referencia)

    def obtener_referencias(self, content_object):
        return self._repo.listar_por_objeto(content_object)

    def obtener_por_id(self, referencia_id):
        return self._repo.obtener_por_id(referencia_id)
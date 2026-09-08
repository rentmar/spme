# spme/spme_fonfosc/services/institucion_service.py
from spme_fonfosc.repositories.institucion_repository import InstitucionRepository
from spme_fonfosc.serializers.institucion_crud_basico_serializer import InstitucionSerializer


class InstitucionService:
    """Servicio para la lógica de negocio de Institucion"""

    @staticmethod
    def listar_instituciones():
        """Listar todas las instituciones serializadas"""
        instituciones = InstitucionRepository.listar_instituciones()
        return InstitucionSerializer(instituciones, many=True).data

    @staticmethod
    def obtener_institucion(institucion_id):
        """Obtener una institución serializada por ID"""
        institucion = InstitucionRepository.obtener_por_id(institucion_id)
        if not institucion:
            return None
        return InstitucionSerializer(institucion).data
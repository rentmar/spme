# spme/spme_fonfosc/repositories/institucion_repository.py
from spme_fonfosc.models import Institucion

class InstitucionRepository:
    """
    Repositorio para el modelo Institucion
    """

    @staticmethod
    def listar_instituciones():
        """Obtener todas las instituciones ordenadas por nombre"""
        return Institucion.objects.all().order_by('nombre')

    @staticmethod
    def obtener_por_id(institucion_id):
        """Obtener una institución por su ID"""
        return Institucion.objects.filter(id=institucion_id).first()
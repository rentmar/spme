# spme/apptran/proyecto/services/actividad_service.py
from django.core.exceptions import ValidationError
from ..repositories.actividad_repository import ActividadRepository

class ActividadService:
    def __init__(self):
        self.repository = ActividadRepository

    def obtener_actividad(self, idactividad):
        actividad = self.repository.get_actividad_por_id(idactividad)
        if not actividad:
            raise ValidationError('Actividad no encontrada')
        return actividad
    
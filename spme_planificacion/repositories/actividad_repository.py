# spme_planificacion/repositories/actividad_repository.py
from spme_actividades.models import Actividad

class ActividadRepository:
    
    def obtener_por_id(self, actividad_id):
        return Actividad.objects.get(id=actividad_id)
    
    def actualizar(self, actividad, datos):
        for campo, valor in datos.items():
            setattr(actividad, campo, valor)
        actividad.save()
        return actividad
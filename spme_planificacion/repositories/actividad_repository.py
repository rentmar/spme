# spme_planificacion/repositories/actividad_repository.py
from spme_actividades.models import Actividad

class ActividadRepository:
    
    def obtener_por_id(self, actividad_id):
        return Actividad.objects.get(id=actividad_id)
    
    #Actualizar actividades
    def actualizar(self, actividad, datos):
        for campo, valor in datos.items():
            setattr(actividad, campo, valor)
        actividad.save()
        return actividad

    #Crear actividades
    def crear(self, datos):
        return Actividad.objects.create(**datos)
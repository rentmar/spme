from ..models import TipoActividad

class TipoActividadDataAccess:
    def __init__(self):
        pass

    def obtenerTiposActividad(self):
        return TipoActividad.objects.all()
    
    def obtenerTipoActividadPorId(self, tipoActividadId):
        return TipoActividad.objects.get(id=tipoActividadId)

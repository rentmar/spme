# spme/spme_planificacion/services/actividad_service.py
from spme_planificacion.repositories.actividad_repository import ActividadRepository
from spme_planificacion.serializers.actividad_serializer import ActividadActualizarSerializer

# services/actividad_service.py
class ActividadService:

    def __init__(self):
        self.repository = ActividadRepository()
    
    def actualizar_actividades(self, actividades_data):
        actualizadas = []
        errores = []
        
        for data in actividades_data:
            try:
                actividad_id = data.get('id')
                serializer = ActividadActualizarSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                datos_limpios = serializer.validated_data
                
                actividad = self.repository.obtener_por_id(actividad_id)
                self.repository.actualizar(actividad, datos_limpios)
                actualizadas.append(actividad_id)
                
            except Exception as e:
                errores.append({'id': data.get('id'), 'error': str(e)})
        
        if errores:
            raise Exception(f"Errores al actualizar actividades: {errores}")
        
        return actualizadas, errores
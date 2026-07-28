# spme/spme_planificacion/services/actividad_service.py
from spme_planificacion.repositories.actividad_repository import ActividadRepository
from spme_planificacion.serializers.actividad_serializer import (
    ActividadActualizarSerializer, 
    ActividadCrearSerializer
)

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

    def crear_actividades(self, actividades_data, proyecto_id):
        creadas = []
        mapeo_ids = {}
        errores = []
        
        for data in actividades_data:
            id_temporal = data.get('id')
            
            try:
                serializer = ActividadCrearSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                datos_limpios = serializer.validated_data
                
                datos_limpios['proyecto_id'] = proyecto_id
                
                actividad = self.repository.crear(datos_limpios)
                
                creadas.append(actividad.id)
                mapeo_ids[id_temporal] = actividad.id
                
            except Exception as e:
                errores.append({'id_temporal': id_temporal, 'error': str(e)})
        
        if errores:
            raise Exception(f"Errores al crear actividades: {errores}")
        
        return creadas, mapeo_ids
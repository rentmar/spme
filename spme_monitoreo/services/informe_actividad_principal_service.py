# spme_monitoreo/services/informe_actividad_principal_service.py
import logging
from spme_monitoreo.models import InformeActividadPrincipal
from spme_actividades.models import Actividad
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)

class InformaActividadPrincipalService:
    """
    Servicio para operaciones CRUD de InformeActividadPrincipal.
    Recibe datos ya validados por el serializer en la vista.
    Métodos estáticos, reutilizables desde cualquier parte del sistema.
    """
    @staticmethod
    def crear(validated_data):
        """
        Crea un nuevo registro en InformeActividadPrincipal.
        
        Args:
            validated_data (dict): Datos ya validados por el serializer.
        
        Returns:
            InformeActividadPrincipal: Instancia creada.
        """
        informe = InformeActividadPrincipal(**validated_data)
        informe.save()
        logger.info(f"InformeActividadPrincipal creado - ID: {informe.id}, Número: {informe.numeroInforme}")
        return informe
    
    @staticmethod
    def actualizar(informe, validated_data):
        """
        Actualiza un registro existente.
        
        Args:
            informe: Instancia de InformeActividadPrincipal.
            validated_data (dict): Datos ya validados a actualizar.
        
        Returns:
            InformeActividadPrincipal: Instancia actualizada.
        """
        for campo, valor in validated_data.items():
            setattr(informe, campo, valor)
        
        informe.save()
        logger.info(f"InformeActividadPrincipal actualizado - ID: {informe.id}")
        return informe
    
    @staticmethod
    def obtener_por_id(informe_id):
        """
        Obtiene un informe por su ID.
        
        Args:
            informe_id (int): ID del informe.
        
        Returns:
            InformeActividadPrincipal o None.
        """
        try:
            return InformeActividadPrincipal.objects.get(id=informe_id)
        except InformeActividadPrincipal.DoesNotExist:
            logger.warning(f"InformeActividadPrincipal con ID {informe_id} no encontrado")
            return None
    
    @staticmethod
    def obtener_por_actividad(actividad_id):
        """
        Obtiene todos los informes de una actividad.
        
        Args:
            actividad_id (int): ID de la actividad.
        
        Returns:
            QuerySet de InformeActividadPrincipal.
        """
        return InformeActividadPrincipal.objects.filter(actividad_id=actividad_id)

    


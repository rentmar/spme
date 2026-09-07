# spme_validaciones/repositories/validacion_solicitud_fondos_repository.py

from .base_repository import BaseValidacionRepository
from ..models import ValidacionSolicitudFondos
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class ValidacionSolicitudFondosRepository(BaseValidacionRepository):
    """
    Repositorio para ValidacionSolicitudFondos.
    """
    def __init__(self):
        super().__init__(ValidacionSolicitudFondos)

    # ===================================================================
    # MÉTODOS EXISTENTES
    # ===================================================================
    
    def obtener_por_solicitud(self, solicitud_id):
        return self.obtener_por_documento(
            documento_id=solicitud_id,
            campo_fk='solicitud',
            select_related=['usuarioValidador', 'usuarioRedactor', 'solicitud']
        )
    
    def obtener_pendientes_por_solicitud(self, solicitud_id):
        return self.obtener_pendientes_por_documento(
            documento_id=solicitud_id,
            campo_fk='solicitud',
            select_related=['usuarioValidador']
        )
    
    def obtener_resumen_estado_solicitud(self, solicitud_id):
        return self.obtener_resumen_estado(
            documento_id=solicitud_id,
            campo_fk='solicitud'
        )

    def obtener_estadisticas_por_solicitud(self, solicitud_id):
        validaciones = self.obtener_por_solicitud(solicitud_id)
        total = validaciones.count()
        
        if total == 0:
            return {
                'total': 0,
                'estado_consolidado': 'SIN_VALIDACIONES',
                'resumen': None,
                'detalle_validadores': []
            }
        
        resumen = self.obtener_resumen_estado_solicitud(solicitud_id)
        
        if resumen['rechazado']:
            estado_consolidado = 'RECHAZADO'
        elif resumen['pendientes'] > 0:
            estado_consolidado = 'PENDIENTE'
        elif resumen['aprobado_totalmente']:
            estado_consolidado = 'APROBADO'
        else:
            estado_consolidado = 'PARCIAL'
        
        detalle = []
        for v in validaciones:
            redactor = v.usuarioRedactor
            detalle.append({
                'validacion_id': v.id,
                'validador_id': v.usuarioValidador_id,
                'validador_nombre': v.usuarioValidador.get_full_name(),
                'estado': v.estado,
                'comentarios': v.comentarios,
                'fecha_asignacion': v.fechaAsignacion,
                'fecha_resolucion': v.fechaResolucion,
                'codigo_seguimiento': v.codigoSeguimiento,
                'version_documento': v.versionDocumento,
                'redactor':{
                    'id': redactor.id,
                    'nombre_completo': redactor.get_full_name(),
                    'email': redactor.correo,  # ✅ CORREGIDO: usar 'correo' no 'email'
                    'rol': redactor.cargo,
                    'username': redactor.username
                }
            })
        
        return {
            'total': total,
            'estado_consolidado': estado_consolidado,
            'resumen': resumen,
            'detalle_validadores': detalle
        }
    
    def obtener_por_validador_con_solicitud(self, usuario_id):
        return self.model_class.objects.filter(
            usuarioValidador_id=usuario_id
        ).select_related(
            'solicitud', 'solicitud__usuario', 'usuarioRedactor'
        ).order_by('-fechaAsignacion')
    
    def obtener_por_solicitante(self, usuario_id):
        return self.model_class.objects.filter(
            usuarioRedactor_id=usuario_id
        ).select_related(
            'solicitud', 'usuarioValidador'
        ).order_by('-fechaAsignacion')
    
    def obtener_pendientes_urgentes(self, usuario_id, horas=24):
        limite = timezone.now() - timedelta(hours=horas)
        return self.model_class.objects.filter(
            usuarioValidador_id=usuario_id,
            estado='PENDIENTE',
            fechaAsignacion__lte=limite
        ).select_related('solicitud').order_by('fechaAsignacion')
    
    # ===================================================================
    # MÉTODOS PARA GESTIÓN DE REVISORES
    # ===================================================================
    
    def obtener_revisores_por_solicitud(self, solicitud_id):
        """
        Obtiene todos los revisores de una solicitud con información completa
        
        Args:
            solicitud_id: ID de la solicitud de fondos
        
        Returns:
            QuerySet de ValidacionSolicitudFondos con relaciones optimizadas
        """
        return self.model_class.objects.filter(
            solicitud_id=solicitud_id
        ).select_related(
            'usuarioValidador',
            'usuarioRedactor',
            'solicitud',
            'solicitud__actividad',
            'solicitud__tarea'
        ).order_by(
            'usuarioValidador__nombre',      # ✅ CORREGIDO
            'usuarioValidador__paterno',     # ✅ CORREGIDO
            'usuarioValidador__materno'      # ✅ CORREGIDO
        )
    
    def obtener_revisor_por_id(self, validacion_id):
        """
        Obtiene una validación específica con información completa del revisor
        
        Args:
            validacion_id: ID de la validación
        
        Returns:
            ValidacionSolicitudFondos o None si no existe
        """
        return self.model_class.objects.select_related(
            'usuarioValidador',
            'usuarioRedactor',
            'solicitud',
            'solicitud__actividad',
            'solicitud__tarea'
        ).filter(id=validacion_id).first()
    
    @transaction.atomic
    def actualizar_revisor(self, validacion_id, nuevo_validador, nueva_version):
        """
        Actualiza el revisor de una validación y resetea el estado
        
        Args:
            validacion_id: ID de la validación
            nuevo_validador: Instancia de Usuario (nuevo revisor)
            nueva_version: String con la nueva versión del documento
        
        Returns:
            Tuple (validacion_actualizada, validador_anterior)
        
        Raises:
            ValueError: Si la validación no existe
        """
        try:
            validacion = self.model_class.objects.select_related(
                'usuarioValidador',
                'solicitud'
            ).get(id=validacion_id)
            
            validador_anterior = validacion.usuarioValidador
            
            # Actualizar revisor y resetear estado
            validacion.usuarioValidador = nuevo_validador
            validacion.estado = 'PENDIENTE'
            validacion.versionDocumento = nueva_version
            validacion.comentarios = ''
            validacion.fechaResolucion = None
            validacion.save()
            
            logger.info(
                f"✅ Revisor actualizado: {validacion_id} - "
                f"{validador_anterior.get_full_name()} → {nuevo_validador.get_full_name()} - "
                f"Versión: {nueva_version}"
            )
            
            return validacion, validador_anterior
            
        except self.model_class.DoesNotExist:
            logger.warning(f"⚠️ Validación {validacion_id} no encontrada")
            raise ValueError(f'Validación {validacion_id} no encontrada')
        except Exception as e:
            logger.error(f"❌ Error actualizando revisor {validacion_id}: {e}", exc_info=True)
            raise
    
    def contar_revisores_por_solicitud(self, solicitud_id):
        """
        Cuenta el número de revisores de una solicitud
        
        Args:
            solicitud_id: ID de la solicitud
        
        Returns:
            int: Número de revisores
        """
        return self.model_class.objects.filter(solicitud_id=solicitud_id).count()
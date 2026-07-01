# spme/spme_validaciones/repositories/base_repository.py
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class BaseValidacionRepository:
    """
    Repositorio base genérico para cualquier tipo de validación.
    """

    def __init__(self, model_class):
        self.model_class = model_class
    
    def obtener_por_id(self, validacion_id, select_related=None):
        queryset = self.model_class.objects.all()
        if select_related: 
            queryset = queryset.select_related(*select_related)
        try: 
            return queryset.get(id=validacion_id)
        except ObjectDoesNotExist: 
            logger.warning(f"Validación {validacion_id} no encontrada en {self.model_class.__name__}")
            return None
    
    def obtener_por_documento(self, documento_id, campo_fk, select_related=None):
        queryset = self.model_class.objects.filter(**{f'{campo_fk}_id': documento_id})
        if select_related: 
            queryset = queryset.select_related(*select_related)
        return queryset.order_by('-fechaAsignacion')
    
    def obtener_por_validador(self, usuario_id, select_related=None):
        queryset = self.model_class.objects.filter(usuarioValidador_id=usuario_id)
        if select_related: 
            queryset = queryset.select_related(*select_related)
        return queryset.order_by('-fechaAsignacion')
    
    def obtener_por_estado(self, documento_id, campo_fk, estado):
        return self.model_class.objects.filter(**{f'{campo_fk}_id': documento_id, 'estado': estado})
    
    def obtener_pendientes_por_documento(self, documento_id, campo_fk, select_related=None):
        return self.obtener_por_estado(documento_id, campo_fk, 'PENDIENTE')
    
    def obtener_resumen_estado(self, documento_id, campo_fk):
        validaciones = self.model_class.objects.filter(**{f'{campo_fk}_id': documento_id})
        total = validaciones.count()
        return {
            'total': total,
            'pendientes': validaciones.filter(estado='PENDIENTE').count(),
            'aprobados': validaciones.filter(estado='APROBADO').count(),
            'rechazados': validaciones.filter(estado='RECHAZADO').count(),
            'completado': validaciones.filter(estado='PENDIENTE').count() == 0 and total > 0,
            'aprobado_totalmente': validaciones.filter(estado='APROBADO').count() == total and total > 0,
            'rechazado': validaciones.filter(estado='RECHAZADO').count() > 0,
        }
    
    @transaction.atomic
    def crear(self, **kwargs):
        validacion = self.model_class(**kwargs)
        validacion.save()
        logger.info(f"✅ Validación creada: {validacion.codigoSeguimiento}")
        return validacion
    
    @transaction.atomic
    def actualizar_estado(self, validacion_id, nuevo_estado, comentarios=None):
        validacion = self.obtener_por_id(validacion_id)
        if not validacion: 
            raise ValueError(f"Validación {validacion_id} no encontrada en {self.model_class.__name__}")
        validacion.estado = nuevo_estado
        if comentarios: 
            validacion.comentarios = comentarios
        validacion.save()
        logger.info(f"✅ Validación actualizada: {validacion.codigoSeguimiento} → {nuevo_estado}")
        return validacion
    
    @transaction.atomic
    def eliminar(self, validacion_id):
        validacion = self.obtener_por_id(validacion_id)
        if not validacion:
            raise ValueError(f"Validación {validacion_id} no encontrada")
        codigo = validacion.codigoSeguimiento
        validacion.delete()
        logger.info(f"🗑️ Validación eliminada: {codigo}")
        return True
    
    def existe_validador(self, documento_id, campo_fk, usuario_validador_id):
        filtro = {
            f'{campo_fk}_id': documento_id,
            'usuarioValidador_id': usuario_validador_id
        }
        return self.model_class.objects.filter(**filtro).exists()
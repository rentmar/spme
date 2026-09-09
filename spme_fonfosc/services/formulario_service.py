# spme/spme_fonfosc/services/formulario_service.py
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from spme_fonfosc.repositories.formulario_repository import FormularioRepository
from spme_fonfosc.models.formulario import Formulario


class FormularioService:
    """Servicio de negocio para formularios"""
    
    def __init__(self, repository: Optional[FormularioRepository] = None):
        self.repository = repository or FormularioRepository()
    
    def get_formulario(self, formulario_id: int) -> Optional[Formulario]:
        """Obtiene un formulario por ID"""
        return self.repository.get_by_id(formulario_id)
    
    def list_formularios(self, usuario=None) -> List[Formulario]:
        """Lista formularios según el usuario"""
        if usuario and not (usuario.is_staff or usuario.is_superuser):
            return self.repository.list_by_user(usuario)
        return self.repository.list_all()
    
    def list_formularios_by_usuario(self, usuario) -> List[Formulario]:
        """Lista formularios de un usuario específico"""
        return self.repository.list_by_user(usuario)
    
    def list_formularios_by_estado(self, estado: str) -> List[Formulario]:
        """Lista formularios por estado"""
        return self.repository.list_by_estado(estado)
    
    def create_formulario(self, data: Dict[str, Any], usuario=None) -> Formulario:
        """
        Crea un nuevo formulario.
        Este método puede ser llamado dentro de una transacción externa.
        """
        self._validate_data(data)
        
        formulario = self.repository.create(data, usuario)
        return formulario
    
    def create_formulario_transaccional(self, data: Dict[str, Any], usuario=None) -> Formulario:
        """
        Crea un formulario dentro de una transacción atómica.
        Útil cuando se necesita crear formularios junto con otros objetos.
        """
        with transaction.atomic():
            return self.create_formulario(data, usuario)
    
    def update_formulario(self, formulario_id: int, data: Dict[str, Any]) -> Optional[Formulario]:
        """Actualiza un formulario existente"""
        formulario = self.repository.get_by_id(formulario_id)
        
        if not formulario:
            raise ValidationError(f"Formulario con ID {formulario_id} no existe")
        
        # No permitir actualizar formularios publicados o archivados
        if formulario.estado in ['published', 'archived']:
            raise ValidationError(f"No se puede actualizar un formulario {formulario.get_estado_display().lower()}")
        
        return self.repository.update(formulario, data)
    
    def update_formulario_transaccional(self, formulario_id: int, data: Dict[str, Any]) -> Optional[Formulario]:
        """Actualiza dentro de transacción con bloqueo"""
        with transaction.atomic():
            formulario = self.repository.get_by_id_for_update(formulario_id)
            
            if not formulario:
                raise ValidationError(f"Formulario con ID {formulario_id} no existe")
            
            if formulario.estado in ['published', 'archived']:
                raise ValidationError(f"No se puede actualizar un formulario {formulario.get_estado_display().lower()}")
            
            return self.repository.update(formulario, data)
    
    def delete_formulario(self, formulario_id: int) -> bool:
        """Elimina un formulario"""
        formulario = self.repository.get_by_id(formulario_id)
        
        if not formulario:
            raise ValidationError(f"Formulario con ID {formulario_id} no existe")
        
        # No permitir eliminar formularios publicados
        if formulario.estado == 'published':
            raise ValidationError("No se puede eliminar un formulario publicado. Archívelo primero.")
        
        return self.repository.delete(formulario)
    
    def delete_formulario_transaccional(self, formulario_id: int) -> bool:
        """Elimina dentro de transacción"""
        with transaction.atomic():
            return self.delete_formulario(formulario_id)
    
    def publicar_formulario(self, formulario_id: int) -> Formulario:
        """Cambia estado a publicado"""
        with transaction.atomic():
            formulario = self.repository.get_by_id_for_update(formulario_id)
            
            if not formulario:
                raise ValidationError(f"Formulario con ID {formulario_id} no existe")
            
            if formulario.estado == 'archived':
                raise ValidationError("No se puede publicar un formulario archivado")
            
            if formulario.estado == 'published':
                raise ValidationError("El formulario ya está publicado")
            
            formulario.estado = 'published'
            formulario.save()
            return formulario
    
    def archivar_formulario(self, formulario_id: int) -> Formulario:
        """Cambia estado a archivado"""
        with transaction.atomic():
            formulario = self.repository.get_by_id_for_update(formulario_id)
            
            if not formulario:
                raise ValidationError(f"Formulario con ID {formulario_id} no existe")
            
            if formulario.estado == 'archived':
                raise ValidationError("El formulario ya está archivado")
            
            formulario.estado = 'archived'
            formulario.save()
            return formulario
    
    def duplicar_formulario(self, formulario_id: int, usuario=None) -> Formulario:
        """
        Duplica un formulario existente como nuevo borrador independiente.
        La copia no está relacionada con el original y la versión se reinicia a 1.
        """
        with transaction.atomic():
            formulario = self.repository.get_by_id(formulario_id)
            
            if not formulario:
                raise ValidationError(f"Formulario con ID {formulario_id} no existe")
            
            # Generar nombre único para la copia
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Crear copia independiente
            nuevo_formulario = Formulario.objects.create(
                nombre=f"{formulario.nombre}_copia_{timestamp}",
                titulo=f"{formulario.titulo} (copia)",
                descripcion=formulario.descripcion,
                version=1,  # Reinicia versión
                estado='draft',  # Siempre como borrador
                definicion_json=formulario.definicion_json,
                creado_por=usuario
            )
            
            return nuevo_formulario
    
    def crear_nueva_version(self, formulario_id: int, usuario=None) -> Formulario:
        """
        Crea una nueva versión del formulario.
        La versión se incrementa y la anterior se archiva si estaba publicada.
        """
        with transaction.atomic():
            formulario = self.repository.get_by_id_for_update(formulario_id)
            
            if not formulario:
                raise ValidationError(f"Formulario con ID {formulario_id} no existe")
            
            # Verificar que no exista ya una versión en borrador
            version_borrador_existente = Formulario.objects.filter(
                nombre=formulario.nombre,
                estado='draft'
            ).exists()
            
            if version_borrador_existente:
                raise ValidationError(
                    f"Ya existe una versión en borrador para este formulario. "
                    f"Termine de editar la versión actual antes de crear una nueva."
                )
            
            # Crear nueva versión
            nueva_version = Formulario.objects.create(
                nombre=formulario.nombre,
                titulo=formulario.titulo,
                descripcion=formulario.descripcion,
                version=formulario.version + 1,  # Incrementar versión
                estado='draft',  # Nueva versión como borrador
                definicion_json=formulario.definicion_json,
                creado_por=usuario
            )
            
            # Archivar la versión anterior si estaba publicada
            if formulario.estado == 'published':
                formulario.estado = 'archived'
                formulario.save()
            
            return nueva_version
    
    def _validate_data(self, data: Dict[str, Any]):
        """Valida datos obligatorios"""
        if not data.get('nombre'):
            raise ValidationError("El campo 'nombre' es obligatorio")
        
        if not data.get('titulo'):
            raise ValidationError("El campo 'titulo' es obligatorio")
        
        if not data.get('definicion_json'):
            raise ValidationError("El campo 'definicion_json' es obligatorio")
# spme/spme_fonfosc/repositories/formulario_repository.py
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from spme_fonfosc.models.formulario import Formulario


class FormularioRepository:
    """Repositorio para operaciones de base de datos del modelo Formulario"""
    
    def get_by_id(self, formulario_id: int) -> Optional[Formulario]:
        """Obtiene un formulario por su ID"""
        try:
            return Formulario.objects.get(id=formulario_id)
        except ObjectDoesNotExist:
            return None
    
    def get_by_id_for_update(self, formulario_id: int) -> Optional[Formulario]:
        """Obtiene un formulario con bloqueo para actualización (dentro de transacción)"""
        try:
            return Formulario.objects.select_for_update().get(id=formulario_id)
        except ObjectDoesNotExist:
            return None
    
    def list_all(self) -> List[Formulario]:
        """Lista todos los formularios"""
        return list(Formulario.objects.all())
    
    def list_by_user(self, usuario) -> List[Formulario]:
        """Lista formularios de un usuario específico"""
        return list(Formulario.objects.filter(creado_por=usuario))
    
    def list_by_estado(self, estado: str) -> List[Formulario]:
        """Lista formularios por estado"""
        return list(Formulario.objects.filter(estado=estado))
    
    def create(self, data: Dict[str, Any], usuario=None) -> Formulario:
        """Crea un nuevo formulario"""
        formulario = Formulario.objects.create(
            nombre=data.get('nombre'),
            titulo=data.get('titulo'),
            descripcion=data.get('descripcion', ''),
            version=data.get('version', 1),
            estado=data.get('estado', 'draft'),
            definicion_json=data.get('definicion_json'),
            creado_por=usuario
        )
        return formulario
    
    def update(self, formulario: Formulario, data: Dict[str, Any]) -> Formulario:
        """Actualiza un formulario existente"""
        for field, value in data.items():
            if hasattr(formulario, field) and field not in ['id', 'creado_por', 'fecha_creacion']:
                setattr(formulario, field, value)
        
        formulario.save()
        return formulario
    
    def delete(self, formulario: Formulario) -> bool:
        """Elimina un formulario"""
        formulario.delete()
        return True
    
    def exists(self, formulario_id: int) -> bool:
        """Verifica si un formulario existe"""
        return Formulario.objects.filter(id=formulario_id).exists()
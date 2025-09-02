from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from ..models import Programa
from ..repositories.programa_repository import ProgramaRepository

class ProgramaService:
    """Servicio de logica de negocio para Programas"""

    #Inicia la clase
    def __init__(self, repository: ProgramaRepository):
        self.repository = repository
    
    #Obtener todos los programas
    def get_all_programas(self)->QuerySet[Programa]:
        return self.repository.get_all()
    
    #Obtener un programa por ID
    def get_programa_by_id(self, programa_id: int) -> Optional[Programa]:
        return self.repository.get_by_id(programa_id)
    
    #Obtener un programa pro codigo
    def get_programa_by_codigo(self, codigo: str) -> Optional[Programa]:
        return self.repository.get_by_codigo(codigo)
    
    #Crear un nuevo programa con validaciones
    def create_programa_(self, programa_data: Dict[str, Any])->Programa:
        #Validar que el nombre no este vacio
        if not programa_data.get('nombre'):
            raise ValueError("El nombre del programa es requerido")
        
        #Validar la longiud del nombre
        if len(programa_data.get('nombre', '')) > 400:
            raise ValueError("El nombre no puede exceder los 400 caracteres")
        
        # Si hay código, validar que sea único
        if programa_data.get('codigo'):
            existing = self.repository.get_by_codigo(programa_data['codigo'])
            if existing:
                raise ValueError("Ya existe un programa con este código")

        return self.repository.create(programa_data)    
    
    def update_programa(self, programa_id: int, programa_data: Dict[str, Any]) -> Optional[Programa]:
        """Actualizar un programa existente"""
        programa = self.repository.get_by_id(programa_id)
        if not programa:
            return None
        
        # Validaciones de negocio
        if 'nombre' in programa_data and not programa_data['nombre']:
            raise ValueError("El nombre del programa es requerido")
        
        if 'nombre' in programa_data and len(programa_data['nombre']) > 400:
            raise ValueError("El nombre no puede exceder los 400 caracteres")
        
        # Validar unicidad del código si se está actualizando
        if 'codigo' in programa_data and programa_data['codigo']:
            existing = self.repository.get_by_codigo(programa_data['codigo'])
            if existing and existing.id != programa_id:
                raise ValueError("Ya existe otro programa con este código")
        
        return self.repository.update(programa, programa_data)
    
    def delete_programa(self, programa_id: int) -> bool:
        """Eliminar un programa"""
        programa = self.repository.get_by_id(programa_id)
        if not programa:
            return False
        
        self.repository.delete(programa)
        return True
    
    def search_programas(self, search_term: str) -> QuerySet[Programa]:
        """Buscar programas por término de búsqueda"""
        if not search_term or len(search_term.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        
        return self.repository.search_by_nombre(search_term.strip())




    


from typing import List, Optional
from django.db.models import QuerySet
from ..models import Programa


class ProgramaRepository:
    """
    Repositorio para operaciones dB para el modelo Programas 
    """
    
    def get_all(self)->QuerySet[Programa]:
        """ Obtener todos los programas """
        return Programa.objects.all()
    
    def get_by_id(self, programa_id:int)->Optional[Programa]: #Optional, la funcion devuelve un obj Programa o nada
        """Obtener un Programa por id"""
        try:
            return Programa.objects.get(id=programa_id)
        except Programa.DoesNotExist:
            return None
        
    def get_by_codigo(self, codigo:str)->Optional[Programa]:
        """Obtener un Programa por Codigo"""
        try:
            return Programa.objects.get(codigo=codigo)
        except Programa.DoesNotExist:
            return None

    def create(self, programa_data:dict)->Programa:
        """Crear un nuevo programa"""
        return Programa.objects.create(**programa_data)

    def update(self, programa: Programa, programa_data: dict) -> Programa:
        """Actualizar un programa existente"""
        for key, value in programa_data.items():
            setattr(programa, key, value)
        programa.save()
        return programa

    def delete(self, programa: Programa) -> None:
        """Eliminar un programa"""
        programa.delete()
    
    def search_by_nombre(self, nombre: str) -> QuerySet[Programa]:
        """Buscar programas por nombre"""
        return Programa.objects.filter(nombre__icontains=nombre).order_by('nombre')    

    

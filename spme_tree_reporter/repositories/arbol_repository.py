# spme/spme_tree_reporter/repositories/arbol_repository.py

"""
ArbolRepository: Único punto de contacto con el árbol jerárquico.
Encapsula la obtención de datos desde spme_repositorio.services.tree.
"""

from spme_repositorio.services.tree import tree_orchestrator


class ArbolRepository:
    """
    Repositorio para obtener estructuras del árbol jerárquico.
    
    Responsabilidades:
    - Invocar al tree_orchestrator
    - Convertir la respuesta a diccionario
    - Manejar errores de conexión
    
    Si en el futuro se cambia la fuente (API HTTP, caché, otro servicio),
    solo se modifica este archivo. El resto del sistema no se entera.
    """
    
    def obtener_arbol(self, tipo_nodo: str, nodo_id: int, profundidad, direccion: str = 'down') -> dict:
        """
        Obtiene el árbol jerárquico desde un nodo específico.
        
        Args:
            tipo_nodo: 'proyecto', 'objetivogeneral', 'actividad', etc.
            nodo_id: ID del nodo
            profundidad: 'self' | 1 | 2 | 3 | 4 | 'all'
            direccion: 'down' | 'up' | 'both'
        
        Returns:
            dict con la estructura del árbol:
            {
                'tipo_nodo': str,
                'id': int,
                'nivel': int,
                'datos': {...},
                'hijos': [...],
                'actividades_relacionadas': [...]
            }
        
        Raises:
            ValueError: Si el nodo no existe o el tipo es inválido
        """
        try:
            response = tree_orchestrator.build_tree(tipo_nodo, nodo_id, profundidad, direccion)
            return response.arbol.to_dict()
        except Exception as e:
            raise ValueError(
                f"Error al obtener árbol para {tipo_nodo}:{nodo_id}. {str(e)}"
            )
    
    def obtener_arbol_proyecto(self, proyecto_id: int, profundidad='all') -> dict:
        """
        Obtiene el árbol completo de un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            profundidad: Niveles a incluir
        
        Returns:
            dict con la estructura completa del proyecto
        """
        return self.obtener_arbol('proyecto', proyecto_id, profundidad, 'down')
    
    def obtener_arbol_actividad(self, actividad_id: int) -> dict:
        """
        Obtiene el árbol completo de una actividad (con tareas, solicitudes, etc.).
        Usado para el anexo de actividades.
        
        Args:
            actividad_id: ID de la actividad
        
        Returns:
            dict con la estructura completa de la actividad
        """
        return self.obtener_arbol('actividad', actividad_id, 'all', 'down')
    
    def obtener_arbol_desde_nodo(self, tipo_nodo: str, nodo_id: int, profundidad='all') -> dict:
        """
        Obtiene el árbol desde cualquier nodo hacia abajo.
        Usado para reportes parciales.
        
        Args:
            tipo_nodo: Tipo de nodo inicial
            nodo_id: ID del nodo
            profundidad: Niveles a incluir
        
        Returns:
            dict con la estructura desde el nodo especificado
        """
        return self.obtener_arbol(tipo_nodo, nodo_id, profundidad, 'down')
    
    def nodo_existe(self, tipo_nodo: str, nodo_id: int) -> bool:
        """
        Verifica si un nodo existe en el árbol.
        
        Args:
            tipo_nodo: Tipo de nodo
            nodo_id: ID del nodo
        
        Returns:
            True si el nodo existe
        """
        try:
            self.obtener_arbol(tipo_nodo, nodo_id, 'self', 'down')
            return True
        except:
            return False
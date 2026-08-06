"""
Contrato base para todos los renderers del árbol.
Cada renderer genera el fragmento Word para UN tipo de nodo.
"""


class BaseRenderer:
    """
    Contrato que deben implementar todos los renderers.
    
    Cada subclase define:
    - tipo_nodo: str que coincide con el tipo_nodo del árbol
    - nivel_heading: nivel de encabezado Word (1-4, 0 = título sin número)
    - requiere_salto_pagina: si agrega salto de página antes de renderizar
    - renderizar_hijos: si el TreeWalker debe recorrer los hijos de este nodo
    """
    
    # === METADATA (sobrescribir en cada subclase) ===
    
    tipo_nodo: str = None
    """Tipo de nodo del árbol. Ej: 'proyecto', 'indicadorog', 'solfondosact'"""
    
    nivel_heading: int = 1
    """Nivel de heading Word. 0=título, 1=Heading1, 2=Heading2, etc."""
    
    requiere_salto_pagina: bool = False
    """Si True, agrega page break antes de renderizar este nodo"""
    
    renderizar_hijos: bool = True
    """Si True, el TreeWalker recorre los hijos. False para nodos hoja."""
    
    # === MÉTODOS (sobrescribir solo si se necesita comportamiento distinto) ===
    
    def render(self, nodo: dict, context) -> None:
        """
        Genera el contenido Word para este nodo.
        
        Args:
            nodo: Diccionario con la estructura del TreeNode:
                {
                    'tipo_nodo': str,
                    'id': int,
                    'nivel': int,
                    'datos': {...},
                    'hijos': [...],
                    'actividades_relacionadas': [...]
                }
            context: ReportContext. Maneja el documento Word y el estado global.
        
        No retorna nada. Modifica context.documento a través de los métodos
        de context (agregar_heading, agregar_tabla_datos, etc.)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} debe implementar render()"
        )
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        """
        Título que se usará en el encabezado numerado.
        Por defecto usa el campo 'codigo' de datos.
        """
        datos = nodo.get('datos', {})
        return datos.get('codigo', datos.get('titulo', 'Sin código'))
    
    def get_actividades(self, nodo: dict) -> list:
        """
        Retorna la lista de actividades_relacionadas del nodo.
        """
        return nodo.get('actividades_relacionadas', [])
    
    def tiene_actividades(self, nodo: dict) -> bool:
        """
        Retorna True si el nodo tiene al menos una actividad relacionada.
        """
        return len(self.get_actividades(nodo)) > 0
    
    # === HELPERS PARA RENDERERS UNIFICADOS ===
    
    def es_de_actividad(self, nodo: dict) -> bool:
        """
        Retorna True si el nodo cuelga directamente de una actividad.
        Útil para renderers que manejan solicitudes/rendiciones tanto
        de actividad como de tarea.
        """
        return nodo.get('tipo_nodo', '').endswith('act')
    
    def es_de_tarea(self, nodo: dict) -> bool:
        """
        Retorna True si el nodo cuelga de una tarea.
        """
        return nodo.get('tipo_nodo', '').endswith('sub')
    
    def get_contexto_nodo(self, nodo: dict) -> str:
        """
        Retorna 'Actividad' o 'Tarea' según el contexto del nodo.
        Útil para construir títulos dinámicos.
        """
        return 'Actividad' if self.es_de_actividad(nodo) else 'Tarea'
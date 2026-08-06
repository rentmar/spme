"""
Renderer para el nodo 'tarea'.
Genera: datos de la tarea y deja que el walker recorra sus hijos.
"""

from .base import BaseRenderer


class TareaRenderer(BaseRenderer):
    """
    Renderer del nodo Tarea.
    
    Contenido que genera:
    - Encabezado con código y título
    - Tabla con datos de la tarea
    
    Sus hijos (solicitudes, rendiciones, informes) los renderiza el walker.
    """
    
    tipo_nodo = 'tarea'
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        datos = nodo.get('datos', {})
        codigo = datos.get('codigo', 'TAR')
        titulo = datos.get('titulo', '')
        return f'Tarea: {codigo} - {titulo}'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        self._render_datos(datos, context)
    
    def _render_datos(self, datos: dict, context) -> None:
        """Tabla con los datos de la tarea."""
        context.agregar_parrafo('Datos de la Tarea', bold=True)
        
        filas = [
            ('Código', datos.get('codigo', '')),
            ('Título', datos.get('titulo', '')),
            ('Estado', datos.get('estado', '')),
            ('Responsable', datos.get('responsable', 'No asignado')),
        ]
        
        context.agregar_tabla_datos(filas)
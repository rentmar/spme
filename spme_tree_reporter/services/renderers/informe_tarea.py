"""
Renderer para el nodo 'informesubactividad'.
"""

from .base import BaseRenderer


class InformeTareaRenderer(BaseRenderer):
    """
    Renderer del nodo Informe de Tarea.
    """
    
    tipo_nodo = 'informesubactividad'
    nivel_heading = 4
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        return 'Informe de Tarea'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        filas = [
            ('Fecha', context.fmt_fecha(datos.get('fecha'))),
            ('Estado', datos.get('estado', '')),
            ('Observaciones', datos.get('observaciones') or 'Sin observaciones'),
        ]
        
        context.agregar_tabla_datos(filas)
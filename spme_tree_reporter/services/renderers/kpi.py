"""
Renderer para el nodo 'kpi'.
Genera: ficha del KPI con código y descripción.
"""

from .base import BaseRenderer


class KPIRenderer(BaseRenderer):
    """
    Renderer del nodo KPI (Key Performance Indicator).
    
    Contenido que genera:
    - Encabezado con código del KPI
    - Descripción / Redacción del KPI
    
    Los KPIs cuelgan directamente del Objetivo General.
    """
    
    tipo_nodo = 'kpi'
    nivel_heading = 2
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'KPI')
        return f'KPI: {codigo}'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        # Encabezado
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        # Código
        codigo = datos.get('codigo', '')
        if codigo:
            context.agregar_parrafo(f'Código: {codigo}', bold=True)
            context.agregar_texto_vacio()
        
        # Descripción / Redacción
        descripcion = datos.get('descripcion', '')
        if descripcion:
            context.agregar_parrafo_destacado(descripcion)
        else:
            context.agregar_parrafo('Sin descripción.')
        
        context.agregar_texto_vacio()
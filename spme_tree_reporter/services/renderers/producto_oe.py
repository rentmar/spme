"""
Renderer para el nodo 'productooe'.
Producto del Objetivo Específico.
"""

from .base import BaseRenderer


class ProductoOERenderer(BaseRenderer):
    """
    Renderer del nodo Producto del Objetivo Específico.
    
    Contenido que genera:
    - Encabezado con código del producto
    - Descripción destacada
    - Actividades vinculadas
    
    Su hijo (proceso POE) lo renderiza el walker.
    """
    
    tipo_nodo = 'productooe'
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'POE')
        return f'PRODUCTO ({codigo})'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        # Encabezado
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        # Descripción
        descripcion = datos.get('descripcion', 'Sin descripción')
        context.agregar_parrafo_destacado(f'"{descripcion}"')
        context.agregar_texto_vacio()
        
        # Actividades vinculadas
        self._render_actividades(nodo, context)
    
    def _render_actividades(self, nodo: dict, context) -> None:
        """Lista de actividades vinculadas al producto."""
        actividades = self.get_actividades(nodo)
        
        if not actividades:
            return
        
        context.agregar_heading('Actividades Vinculadas', self.nivel_heading + 1)
        
        for act in actividades:
            texto = f"{act['codigo']}: \"{act['nombre']}\""
            if context.modo_actividades == 'anexo':
                texto += ' (Ver Anexo)'
            context.agregar_viñeta(texto)
        
        context.agregar_texto_vacio()
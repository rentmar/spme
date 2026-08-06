"""
Renderer para el nodo 'productoroe'.
Producto del Resultado del Objetivo Específico.
"""

from .base import BaseRenderer


class ProductoROERenderer(BaseRenderer):
    """
    Renderer del nodo Producto de Resultado OE.
    
    Misma estructura que ProductoOE pero en nivel 4.
    """
    
    tipo_nodo = 'productoroe'
    nivel_heading = 4
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'PROE')
        return f'PRODUCTO ({codigo})'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        descripcion = datos.get('descripcion', 'Sin descripción')
        context.agregar_parrafo_destacado(f'"{descripcion}"')
        context.agregar_texto_vacio()
        
        self._render_actividades(nodo, context)
    
    def _render_actividades(self, nodo: dict, context) -> None:
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
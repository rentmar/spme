"""
Renderer para el nodo 'resultadooe'.
Resultado del Objetivo Específico.
"""

from .base import BaseRenderer


class ResultadoOERenderer(BaseRenderer):
    """
    Renderer del nodo Resultado del Objetivo Específico.
    
    Misma estructura que ResultadoOG pero en nivel 3.
    
    Sus hijos (indicadores ROE, productos ROE, procesos ROE) los renderiza el walker.
    """
    
    tipo_nodo = 'resultadooe'
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'ROE')
        return f'RESULTADO ({codigo})'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        # Encabezado
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        # Descripción
        descripcion = datos.get('descripcion', 'Sin descripción')
        context.agregar_parrafo_destacado(f'"{descripcion}"')
        context.agregar_texto_vacio()
        
        # Supuestos y Riesgos
        self._render_supuestos_riesgos(datos, context)
        
        # Actividades vinculadas
        self._render_actividades(nodo, context)
    
    def _render_supuestos_riesgos(self, datos: dict, context) -> None:
        """Tabla con supuestos y riesgos."""
        context.agregar_heading('Supuestos y Riesgos', self.nivel_heading + 1)
        
        filas = [
            ('Supuestos', datos.get('supuestos') or 'No especificados'),
            ('Riesgos', datos.get('riesgos') or 'No especificados'),
        ]
        
        context.agregar_tabla_datos(filas)
    
    def _render_actividades(self, nodo: dict, context) -> None:
        """Lista de actividades vinculadas."""
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
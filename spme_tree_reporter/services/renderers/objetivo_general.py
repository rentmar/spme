# spme/spme_tree_reporter/services/renderers/objetivo_general.py
"""
Renderer para el nodo 'objetivogeneral'.
Genera: descripción, supuestos/riesgos, y lista de actividades vinculadas.
"""

from .base import BaseRenderer


class ObjetivoGeneralRenderer(BaseRenderer):
    """
    Renderer del nodo Objetivo General.
    
    Contenido que genera:
    - Encabezado con código del OG
    - Descripción destacada
    - Tabla de Supuestos y Riesgos
    - Lista de actividades vinculadas (referencia)
    """
    
    tipo_nodo = 'objetivogeneral'
    nivel_heading = 1
    requiere_salto_pagina = True
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'OG')
        return f'OBJETIVO GENERAL ({codigo})'
    
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
        
        # Los hijos (KPIs, indicadores, resultados, objetivos específicos)
        # los renderizará el walker automáticamente
    
    def _render_supuestos_riesgos(self, datos: dict, context) -> None:
        """Tabla con supuestos y riesgos del objetivo general."""
        context.agregar_heading('Supuestos y Riesgos', self.nivel_heading + 1)
        
        filas = [
            ('Supuestos', datos.get('supuestos') or 'No especificados'),
            ('Riesgos', datos.get('riesgos') or 'No especificados'),
        ]
        
        context.agregar_tabla_datos(filas)
    
    def _render_actividades(self, nodo: dict, context) -> None:
        """Lista de actividades vinculadas directamente al objetivo general."""
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
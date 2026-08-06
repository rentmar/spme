# spme/spme_tree_reporter/services/renderers/proceso.py
"""
Renderer para los nodos de tipo 'proceso'.
Maneja: procesorog, procesooe, procesopoe, procesoroe.
"""

from .base import BaseRenderer


class ProcesoRenderer(BaseRenderer):
    """
    Renderer para todos los tipos de proceso.
    
    Contenido que genera:
    - Encabezado con código del proceso
    - Título y descripción
    - Actividades vinculadas
    
    El nivel de heading varía según dónde está en el árbol:
    - Proceso ROG: nivel 3 (hijo de resultado OG)
    - Proceso OE: nivel 3 (hijo de objetivo específico)
    - Proceso POE: nivel 4 (hijo de producto OE)
    - Proceso ROE: nivel 4 (hijo de resultado OE)
    """
    
    tipo_nodo = 'proceso'  # Genérico, se registra para los 4 tipos
    requiere_salto_pagina = False
    renderizar_hijos = False  # Los procesos son nodos hoja
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'PROC')
        return f'Proceso: {codigo}'
    
    @property
    def nivel_heading(self):
        """
        El nivel depende del tipo de proceso.
        Los procesos ROG y OE van en nivel 3.
        Los procesos POE y ROE van en nivel 4.
        """
        return 3  # Por defecto. Se ajusta en render() si es necesario.
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        tipo = nodo.get('tipo_nodo', '')
        
        # Ajustar nivel según tipo de proceso
        if tipo in ('procesopoe', 'procesoroe'):
            nivel = 4
        else:
            nivel = 3
        
        # Encabezado
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, nivel)
        
        # Título del proceso
        titulo_proceso = datos.get('titulo', '')
        if titulo_proceso:
            context.agregar_parrafo_destacado(titulo_proceso)
            context.agregar_texto_vacio()
        
        # Descripción
        descripcion = datos.get('descripcion', '')
        if descripcion:
            context.agregar_parrafo(descripcion)
            context.agregar_texto_vacio()
        
        # Si no hay título ni descripción
        if not titulo_proceso and not descripcion:
            context.agregar_parrafo('Sin información adicional.')
            context.agregar_texto_vacio()
        
        # Actividades vinculadas
        self._render_actividades(nodo, context)
    
    def _render_actividades(self, nodo: dict, context) -> None:
        """Lista de actividades vinculadas al proceso."""
        actividades = self.get_actividades(nodo)
        
        if not actividades:
            return
        
        context.agregar_parrafo('Actividades Vinculadas', bold=True)
        
        for act in actividades:
            texto = f"{act['codigo']}: \"{act['nombre']}\""
            if context.modo_actividades == 'anexo':
                texto += ' (Ver Anexo)'
            context.agregar_viñeta(texto)
        
        context.agregar_texto_vacio()
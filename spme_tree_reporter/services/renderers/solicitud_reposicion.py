"""
Renderer para reposiciones.
Maneja: solreposicionact, solreposicionsub.
"""

from .base import BaseRenderer


class SolicitudReposicionRenderer(BaseRenderer):
    """
    Renderer unificado para Reposición.
    """
    
    tipo_nodo = None
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        contexto = self.get_contexto_nodo(nodo)
        
        titulo = f'Reposición ({contexto})'
        context.agregar_heading(titulo, self.nivel_heading)
        
        filas = [
            ('Monto', context.fmt_monto(datos.get('monto'))),
            ('Estado', datos.get('estado', '')),
            ('Fecha', context.fmt_fecha(datos.get('fecha'))),
        ]
        
        context.agregar_tabla_datos(filas)
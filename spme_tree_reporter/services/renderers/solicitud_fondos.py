"""
Renderer para solicitudes de fondos.
Maneja: solfondosact, solfondossub.
"""

from .base import BaseRenderer


class SolicitudFondosRenderer(BaseRenderer):
    """
    Renderer unificado para Solicitud de Fondos.
    
    Si el nodo es 'solfondosact' → Solicitud de la Actividad
    Si el nodo es 'solfondossub' → Solicitud de la Tarea
    """
    
    tipo_nodo = None
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        contexto = self.get_contexto_nodo(nodo)
        
        titulo = f'Solicitud de Fondos ({contexto})'
        context.agregar_heading(titulo, self.nivel_heading)
        
        filas = [
            ('Monto Solicitado', context.fmt_monto(datos.get('monto'))),
            ('Estado', datos.get('estado', '')),
            ('Fecha', context.fmt_fecha(datos.get('fecha'))),
        ]
        
        context.agregar_tabla_datos(filas)
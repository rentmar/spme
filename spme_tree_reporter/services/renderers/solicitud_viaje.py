"""
Renderer para solicitudes de viaje.
Maneja: solviajeact, solviajesub.
"""

from .base import BaseRenderer


class SolicitudViajeRenderer(BaseRenderer):
    """
    Renderer unificado para Solicitud de Viaje.
    """
    
    tipo_nodo = None
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        contexto = self.get_contexto_nodo(nodo)
        
        titulo = f'Solicitud de Viaje ({contexto})'
        context.agregar_heading(titulo, self.nivel_heading)
        
        filas = [
            ('Destino', datos.get('destino', '')),
            ('Monto', context.fmt_monto(datos.get('monto'))),
            ('Estado', datos.get('estado', '')),
            ('Fecha', context.fmt_fecha(datos.get('fecha'))),
        ]
        
        context.agregar_tabla_datos(filas)
"""
Renderer para rendiciones de cuentas.
Maneja: rendicioncuentasact, rendicioncuentassub.
"""

from .base import BaseRenderer


class RendicionCuentasRenderer(BaseRenderer):
    """
    Renderer unificado para Rendición de Cuentas.
    """
    
    tipo_nodo = None
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        contexto = self.get_contexto_nodo(nodo)
        
        titulo = f'Rendición de Cuentas ({contexto})'
        context.agregar_heading(titulo, self.nivel_heading)
        
        filas = [
            ('Monto Rendido', context.fmt_monto(datos.get('monto_rendido'))),
            ('Monto Aprobado', context.fmt_monto(datos.get('monto_aprobado'))),
            ('Estado', datos.get('estado', '')),
            ('Fecha', context.fmt_fecha(datos.get('fecha'))),
        ]
        
        context.agregar_tabla_datos(filas)
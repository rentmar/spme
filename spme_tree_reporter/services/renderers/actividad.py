"""
Renderer para el nodo 'actividad'.
Genera: datos generales de la actividad y deja que el walker recorra sus hijos.
"""

from .base import BaseRenderer


class ActividadRenderer(BaseRenderer):
    """
    Renderer del nodo Actividad.
    
    Contenido que genera:
    - Encabezado con código y nombre
    - Tabla con datos generales (estado, responsable, fechas)
    
    Sus hijos (solicitudes, rendiciones, informes, tareas) los renderiza el walker.
    """
    
    tipo_nodo = 'actividad'
    nivel_heading = 2
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        datos = nodo.get('datos', {})
        codigo = datos.get('codigo', 'ACT')
        nombre = datos.get('nombre', '')
        return f'ACTIVIDAD: {codigo} - {nombre}'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        # Encabezado
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        # Datos generales
        self._render_datos_generales(datos, context)
    
    def _render_datos_generales(self, datos: dict, context) -> None:
        """Tabla con los datos principales de la actividad."""
        context.agregar_parrafo('Datos Generales', bold=True)
        
        filas = [
            ('Código', datos.get('codigo', '')),
            ('Nombre', datos.get('nombre', '')),
            ('Estado', datos.get('estado', '')),
            ('Responsable', datos.get('responsable', 'No asignado')),
            ('Fecha de Inicio', context.fmt_fecha(datos.get('fecha_inicio'))),
            ('Fecha de Fin', context.fmt_fecha(datos.get('fecha_fin'))),
        ]
        
        context.agregar_tabla_datos(filas)
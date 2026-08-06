# spme/spme_tree_reporter/services/renderers/proyecto.py

"""
Renderer para el nodo 'proyecto'.
Genera: portada, datos generales, gobernanza y financiamiento.
"""
from .base import BaseRenderer


class ProyectoRenderer(BaseRenderer):
    tipo_nodo = 'proyecto'
    nivel_heading = 0
    requiere_salto_pagina = False
    renderizar_hijos = True
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        incluir_portada = context.config.get('incluir_portada', True)
        incluir_indice = context.config.get('incluir_indice', True)
        
        if incluir_portada:
            self._render_portada(datos, context)
            context.agregar_salto_pagina()
        
        if incluir_indice:
            self._render_indice(context)
            context.agregar_salto_pagina()
        
        context.agregar_heading('DATOS GENERALES DEL PROYECTO', 1)
        self._render_identificacion(datos, context)
        self._render_temporalidad(datos, context)
        self._render_gobernanza(datos, context)
        self._render_financiamiento(datos, context)
        context.agregar_salto_pagina()
    
    def _render_portada(self, datos, context):
        for _ in range(6):
            context.agregar_texto_vacio()
        context.agregar_parrafo('REPORTE DE PROYECTO', bold=True, alineacion='center')
        context.agregar_texto_vacio()
        context.agregar_titulo(datos.get('codigo', 'Sin código'))
        context.agregar_parrafo(datos.get('titulo', 'Sin título'), alineacion='center')
        context.agregar_texto_vacio()
        context.agregar_texto_vacio()
        context.agregar_parrafo(f"PEI: {datos.get('pei', 'No especificado')}", alineacion='center')
        context.agregar_parrafo(f"Estado: {datos.get('estado', 'No especificado')}", alineacion='center')
        context.agregar_parrafo(f"Propietario: {datos.get('propietario', 'No asignado')}", alineacion='center')
        context.agregar_texto_vacio()
        context.agregar_texto_vacio()
        from datetime import date
        context.agregar_parrafo(f"Generado el {date.today().strftime('%d/%m/%Y')}", alineacion='center')
    
    def _render_indice(self, context):
        context.agregar_heading('ÍNDICE DE CONTENIDOS', 1)
        context.agregar_texto_vacio()
        context.agregar_parrafo(
            '[Actualizar índice: hacer clic derecho sobre esta sección y seleccionar '
            '"Actualizar campo" en Microsoft Word]',
            italic=True
        )
    
    def _render_identificacion(self, datos, context):
        context.agregar_heading('Identificación', 2)
        filas = [
            ('Código', datos.get('codigo', '')),
            ('Título', datos.get('titulo', '')),
            ('Descripción', datos.get('descripcion', '')),
            ('PEI', datos.get('pei', 'No especificado')),
            ('Programa', datos.get('programa') or 'No asignado'),
            ('Propietario', datos.get('propietario', '')),
        ]
        context.agregar_tabla_datos(filas)
    
    def _render_temporalidad(self, datos, context):
        context.agregar_heading('Temporalidad y Presupuesto', 2)
        fecha_inicio = datos.get('fecha_inicio', '')
        fecha_fin = datos.get('fecha_finalizacion', '')
        filas = [
            ('Fecha de Inicio', context.fmt_fecha(fecha_inicio)),
            ('Fecha de Finalización', context.fmt_fecha(fecha_fin)),
            ('Duración', context.fmt_duracion(fecha_inicio, fecha_fin)),
            ('Presupuesto', context.fmt_monto(datos.get('presupuesto', '0'))),
            ('Estado', datos.get('estado', '')),
        ]
        context.agregar_tabla_datos(filas)
    
    def _render_gobernanza(self, datos, context):
        context.agregar_heading('Gobernanza', 2)
        instancias = datos.get('instancias_gestoras', [])
        if instancias:
            context.agregar_parrafo('Instancias Gestoras:', bold=True)
            for instancia in instancias:
                context.agregar_viñeta(str(instancia))
        else:
            context.agregar_parrafo('No se han definido instancias gestoras.')
        context.agregar_texto_vacio()
    
    def _render_financiamiento(self, datos, context):
        context.agregar_heading('Financiamiento', 2)
        procedencias = datos.get('procedencia_fondos', [])
        if procedencias:
            headers = ['Sigla', 'Entidad Financiera']
            filas = []
            for p in procedencias:
                filas.append([p.get('sigla', ''), p.get('financiera', '')])
            context.agregar_tabla(headers, filas, titulo='Procedencia de Fondos')
        else:
            context.agregar_parrafo('No se ha definido procedencia de fondos.')
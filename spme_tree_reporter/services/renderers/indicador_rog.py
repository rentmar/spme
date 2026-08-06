# spme/spme_tree_reporter/services/renderers/indicador_rog.py
"""
Renderer para el nodo 'indicadorrog'.
Indicador de Resultado del Objetivo General.
"""

from .base import BaseRenderer


class IndicadorROGRenderer(BaseRenderer):
    """
    Renderer del nodo Indicador de Resultado OG.
    
    Misma estructura que IndicadorOG pero en nivel 3.
    La bitácora se integrará cuando tengamos el BitacoraRepository.
    """
    
    tipo_nodo = 'indicadorrog'
    nivel_heading = 3
    requiere_salto_pagina = False
    renderizar_hijos = False
    
    def get_titulo_seccion(self, nodo: dict) -> str:
        codigo = nodo.get('datos', {}).get('codigo', 'IND-ROG')
        return f'Indicador: {codigo}'
    
    def render(self, nodo: dict, context) -> None:
        datos = nodo.get('datos', {})
        
        titulo = self.get_titulo_seccion(nodo)
        context.agregar_heading(titulo, self.nivel_heading)
        
        self._render_ficha_tecnica(datos, context)
        self._render_metas(datos, context)
        
        # TODO: Cuando se implemente BitacoraRepository, agregar:
        # from ...repositories.bitacora_repository import BitacoraRepository
        # bitacora_repo = BitacoraRepository()
        # entradas = bitacora_repo.obtener_bitacora('indicadorrog', nodo['id'])
        # self._render_bitacora(entradas, context)
        
        self._render_actividades(nodo, context)
    
    def _render_ficha_tecnica(self, datos: dict, context) -> None:
        context.agregar_parrafo('Ficha Técnica', bold=True)
        
        filas = [
            ('Descripción', datos.get('descripcion', '')),
            ('Tipo', datos.get('tipo', '')),
            ('Frecuencia', datos.get('frecuencia', '')),
            ('Redacción', datos.get('redaccion', '')),
            ('Fuente de Verificación', datos.get('fuente_verificacion', '')),
            ('Línea Base', datos.get('baseline') or 'No especificada'),
        ]
        
        context.agregar_tabla_datos(filas)
    
    def _render_metas(self, datos: dict, context) -> None:
        metas = {
            'Q1': datos.get('target_q1'),
            'Q2': datos.get('target_q2'),
            'Q3': datos.get('target_q3'),
            'Q4': datos.get('target_q4'),
        }
        
        if not any(metas.values()):
            return
        
        context.agregar_parrafo('Metas Trimestrales', bold=True)
        
        headers = ['Trimestre', 'Meta']
        filas = [[t, m or 'No especificada'] for t, m in metas.items()]
        
        context.agregar_tabla(headers, filas)
    
    # TODO: Descomentar cuando exista BitacoraRepository
    # def _render_bitacora(self, entradas: list, context) -> None:
    #     """Tabla con el historial de mediciones del indicador."""
    #     if not entradas:
    #         return
    #     
    #     context.agregar_parrafo('Bitácora de Mediciones', bold=True)
    #     
    #     headers = ['Fecha', 'Valor', 'Avance %', 'Registrado por']
    #     filas = []
    #     for entrada in entradas:
    #         filas.append([
    #             context.fmt_fecha(entrada.get('fecha')),
    #             entrada.get('valor', ''),
    #             entrada.get('avance', ''),
    #             entrada.get('usuario', ''),
    #         ])
    #     
    #     context.agregar_tabla(headers, filas)
    
    def _render_actividades(self, nodo: dict, context) -> None:
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
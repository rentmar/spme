from .base import BaseRenderer
class IndicadorOGRenderer(BaseRenderer):
    tipo_nodo = 'indicadorog'
    nivel_heading = 2
    requiere_salto_pagina = False
    renderizar_hijos = False
    def render(self, nodo, context):
        pass

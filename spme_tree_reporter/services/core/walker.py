"""
TreeWalker: Recorre el árbol jerárquico en pre-orden y dispara los renderers.
"""


class TreeWalker:
    """
    Recorre el árbol en pre-orden (padre → hijos en secuencia).
    Por cada nodo, invoca al renderer correspondiente del registry.
    
    Responsabilidades:
    - Recorrer el árbol respetando la propiedad renderizar_hijos de cada renderer
    - Recolectar actividades_relacionadas para el anexo
    - Generar el anexo de actividades al final del recorrido
    
    No genera contenido Word directamente. Eso lo hacen los renderers.
    """
    
    def __init__(self, context, renderer_registry, arbol_repo):
        """
        Args:
            context: ReportContext (documento Word + estado)
            renderer_registry: RendererRegistry (mapeo tipo_nodo → renderer)
            arbol_repo: ArbolRepository (para expandir actividades en anexo)
        """
        self.context = context
        self.registry = renderer_registry
        self.arbol_repo = arbol_repo
    
    # =====================================================================
    # RECORRIDO PRINCIPAL
    # =====================================================================
    
    def walk(self, nodo: dict, nivel: int = 0):
        """
        Recorrido pre-orden del árbol.
        
        Orden:
        1. Renderizar el nodo actual
        2. Si el renderer lo permite, recorrer todos sus hijos
        3. Recolectar actividades_relacionadas para el anexo
        
        Args:
            nodo: Diccionario TreeNode desde el árbol
            nivel: Profundidad actual (0 = raíz)
        """
        tipo = nodo.get('tipo_nodo')
        renderer = self.registry.get(tipo)
        
        # 1. Renderizar nodo actual
        if renderer:
            # Salto de página antes si el renderer lo pide
            if renderer.requiere_salto_pagina and nivel > 0:
                self.context.agregar_salto_pagina()
            
            renderer.render(nodo, self.context)
        
        # 2. Recorrer hijos (si el renderer no lo impide)
        if not renderer or renderer.renderizar_hijos:
            for hijo in nodo.get('hijos', []):
                self.walk(hijo, nivel + 1)
        
        # 3. Recolectar actividades para anexo
        if self.context.modo_actividades == 'anexo':
            self._recolectar_actividades(nodo)
    
    # =====================================================================
    # RECOLECCIÓN DE ACTIVIDADES
    # =====================================================================
    
    def _recolectar_actividades(self, nodo: dict):
        """
        Acumula referencias únicas de actividades_relacionadas.
        
        Estructura acumulada:
        {
            act_id: {
                'data': {...},       # Info básica de la actividad
                'vinculaciones': [   # Dónde aparece vinculada
                    {'tipo_nodo': 'indicadorog', 'nombre': 'IND0001-OO'},
                    ...
                ]
            }
        }
        """
        for act in nodo.get('actividades_relacionadas', []):
            act_id = act['id']
            
            # Primera vez que vemos esta actividad
            if act_id not in self.context._actividades_anexo:
                self.context._actividades_anexo[act_id] = {
                    'data': act,
                    'vinculaciones': []
                }
            
            # Registrar dónde está vinculada
            nombre_nodo = nodo.get('datos', {}).get('codigo', '')
            if not nombre_nodo:
                nombre_nodo = nodo.get('datos', {}).get('titulo', '')
            
            self.context._actividades_anexo[act_id]['vinculaciones'].append({
                'tipo_nodo': nodo['tipo_nodo'],
                'nombre': nombre_nodo
            })
    
    # =====================================================================
    # ANEXO DE ACTIVIDADES
    # =====================================================================
    
    def generar_anexo_actividades(self):
        """
        Genera el anexo con el detalle completo de todas las actividades
        recolectadas durante el recorrido.
        
        Se llama DESPUÉS de walk().
        Cada actividad se expande invocando al árbol y se renderiza completa.
        """
        actividades = self.context._actividades_anexo
        
        if not actividades:
            return
        
        # Título del anexo
        self.context.agregar_salto_pagina()
        self.context.agregar_heading('ANEXO: DETALLE DE ACTIVIDADES VINCULADAS', 1)
        
        total = len(actividades)
        
        for i, (act_id, act_info) in enumerate(actividades.items(), 1):
            # Obtener árbol completo de la actividad
            act_tree = self.arbol_repo.obtener_arbol_actividad(act_id)
            
            # Renderizar actividad
            renderer = self.registry.get('actividad')
            if renderer:
                letra = chr(64 + i)  # A, B, C, ...
                self.context.agregar_heading(
                    f'{letra}. {act_info["data"]["codigo"]}: {act_info["data"]["nombre"]}',
                    2
                )
                renderer.render(act_tree, self.context)
                
                # Mostrar vinculaciones (dónde aparece esta actividad)
                self.context.agregar_texto_vacio()
                self.context.agregar_parrafo('Vinculada a:', bold=True)
                for v in act_info['vinculaciones']:
                    self.context.agregar_viñeta(
                        f"{v['tipo_nodo']}: {v['nombre']}"
                    )
                
                # Salto de página entre actividades (excepto la última)
                if i < total:
                    self.context.agregar_salto_pagina()
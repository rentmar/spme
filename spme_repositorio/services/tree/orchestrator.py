 # Coordinador principal
from typing import Optional, Dict, List
from .dto import TreeNode, TreeMetadata, TreeResponse, BuildContext
from .registry import NodeRegistry
from .depth_strategy import DepthStrategy
from .enums import Direction
from django.apps import apps
from .base import BaseNodeBuilder
from .enums import NodeType

class TreeOrchestrator:
    """
    Orquestador principal del sistema de árbol.
    
    Coordina:
    - Resolución de builders vía Registry
    - Control de profundidad vía DepthStrategy
    - Navegación bidireccional (up/down/both)
    - Ensamblado de respuesta final
    """
    
    def __init__(self, registry: NodeRegistry):
        self.registry = registry

    def _cargar_actividades_proyecto(self, proyecto_id) -> Dict[str, List[Dict]]:
        """
        Carga todas las actividades activas del proyecto y las indexa
        por node_type:node_id usando su estructuraProcedencia.
        
        Returns:
            Diccionario: {"objetivogeneral:44": [{id, codigo, ...}], ...}
        """
        print(f"\n[DEBUG CARGA ACTIVIDADES] Cargando actividades del proyecto {proyecto_id}")
        
        try:
            Actividad = apps.get_model('spme_actividades', 'Actividad')
            
            actividades = Actividad.objects.filter(
                proyecto_id=proyecto_id,
                estaInactiva=False
            ).only('id', 'codigo', 'nombreCorto', 'estructuraProcedencia')
            
            print(f"[DEBUG CARGA ACTIVIDADES] Encontradas: {actividades.count()} actividades activas")
            
            index = {}
            
            for actividad in actividades:
                print(f"\n[DEBUG CARGA ACTIVIDADES] Procesando Actividad ID={actividad.id}, Código={actividad.codigo}")
                
                if not actividad.estructuraProcedencia:
                    print(f"[DEBUG CARGA ACTIVIDADES]   Sin estructuraProcedencia, saltando")
                    continue
                
                selecciones = actividad.estructuraProcedencia.get('seleccionesSimples', {})
                print(f"[DEBUG CARGA ACTIVIDADES]   seleccionesSimples: {selecciones}")
                
                # Recorrer el mapeo para indexar esta actividad
                for node_type, config in BaseNodeBuilder.SELECCIONES_MAPPING.items():
                    campo = config['campo']
                    es_array = config['es_array']
                    
                    if campo not in selecciones:
                        continue
                    
                    valor = selecciones[campo]
                    
                    if es_array and isinstance(valor, list):
                        for v in valor:
                            key = f"{node_type}:{v}"
                            if key not in index:
                                index[key] = []
                            index[key].append({
                                'id': actividad.id,
                                'codigo': actividad.codigo or '',
                                'nombre': actividad.nombreCorto or '',
                                'tipo_nodo': 'actividad'
                            })
                            print(f"[DEBUG CARGA ACTIVIDADES]   Indexado: '{key}'")
                    elif not es_array and valor is not None:
                        key = f"{node_type}:{valor}"
                        if key not in index:
                            index[key] = []
                        index[key].append({
                            'id': actividad.id,
                            'codigo': actividad.codigo or '',
                            'nombre': actividad.nombreCorto or '',
                            'tipo_nodo': 'actividad'
                        })
                        print(f"[DEBUG CARGA ACTIVIDADES]   Indexado: '{key}'")
            
            print(f"\n[DEBUG CARGA ACTIVIDADES] Índice final: {len(index)} claves")
            for k, v in index.items():
                print(f"[DEBUG CARGA ACTIVIDADES]   {k}: {len(v)} actividades")
            
            return index
            
        except Exception as e:
            print(f"[DEBUG CARGA ACTIVIDADES] Error: {e}")
            return {}

    
    def build_tree(
        self,
        node_type: str,
        node_id,
        depth: str = 'all',
        direction: str = 'down'
    ) -> TreeResponse:
        """
        Construye el árbol jerárquico según los parámetros.
        
        Args:
            node_type: Tipo de nodo inicial
            node_id: ID del nodo inicial
            depth: Profundidad ('self', '1', '2', ..., 'all')
            direction: Dirección ('down', 'up', 'both')
            
        Returns:
            TreeResponse con el árbol y metadata
        """
        if not self.registry.has_builder(node_type):
            raise ValueError(f"Tipo de nodo no soportado: {node_type}")
        
        depth_strategy = DepthStrategy(depth)
        
        # Cargar actividades si es un proyecto
        actividades_index = {}
        if node_type == NodeType.PROYECTO.value:
            print(f"\n[DEBUG ORCH] Iniciando árbol desde proyecto {node_id}")
            actividades_index = self._cargar_actividades_proyecto(node_id)
        elif node_type == 'proyecto':
            print(f"\n[DEBUG ORCH] Iniciando árbol desde proyecto {node_id}")
            actividades_index = self._cargar_actividades_proyecto(node_id)
        
        # Crear contexto
        context = BuildContext(
            node_type=node_type,
            node_id=node_id,
            depth=depth,
            direction=direction,
            actividades_index=actividades_index
        )
        
        # Construir según dirección (pasando context)
        if direction == Direction.DOWN:
            root, _ = self._build_down(node_type, node_id, depth_strategy, context=context)
        elif direction == Direction.UP:
            root, _ = self._build_up(node_type, node_id, depth_strategy, context=context)
        elif direction == Direction.BOTH:
            root, _ = self._build_both(node_type, node_id, depth_strategy, context=context)
        else:
            raise ValueError(f"Dirección no soportada: {direction}")
        
        total_nodos = self._count_all_nodes(root) if root else 0
        profundidad_alcanzada = self._calculate_max_depth(root)
        
        metadata = TreeMetadata(
            nodo_inicio=f"{node_type}:{node_id}",
            profundidad_solicitada=depth,
            profundidad_alcanzada=profundidad_alcanzada,
            total_nodos=total_nodos,
            direccion=direction,
            estructura=self.registry.get_structure_description(node_type)
        )
        
        return TreeResponse(arbol=root, metadata=metadata)
    
    def _count_all_nodes(self, nodo: TreeNode) -> int:
        """Cuenta todos los nodos en el árbol recursivamente"""
        if nodo is None:
            return 0
        count = 1
        for hijo in nodo.hijos:
            count += self._count_all_nodes(hijo)
        return count
    
    def _build_down(
        self,
        node_type: str,
        node_id,
        depth_strategy: DepthStrategy,
        nivel: int = 0,
        es_nodo_objetivo: bool = True,
        context: BuildContext = None  # ← NUEVO
    ) -> tuple:
        total_nodos = 0
        
        builder = self.registry.get_builder(node_type)
        nodo = builder.build(
            node_id=node_id,
            nivel=nivel,
            es_nodo_objetivo=es_nodo_objetivo,
            build_context=context  # ← NUEVO
        )
        total_nodos += 1
        
        if depth_strategy.is_self_only():
            return nodo, total_nodos
        
        if depth_strategy.should_continue(nivel):
            children_types = self.registry.get_children_types(node_type)
            
            # Crear sub-contexto para hijos
            child_context = context.increment_level() if context else None
            
            for child_type in children_types:
                child_nodes = self._build_children(
                    parent_nodo=nodo,
                    child_type=child_type,
                    depth_strategy=depth_strategy,
                    nivel_actual=nivel,
                    context=child_context  # ← NUEVO
                )
                nodo.hijos.extend(child_nodes)
                total_nodos += len(child_nodes)
        
        return nodo, total_nodos   

    def _build_up(
        self,
        node_type: str,
        node_id,
        depth_strategy: DepthStrategy,
        nivel: int = 0
    ) -> tuple:
        """
        Construye el árbol hacia arriba (ancestros).
        El nodo solicitado es la HOJA final.
        """
        total_nodos = 0
        
        # Construir nodo actual (el solicitado)
        builder = self.registry.get_builder(node_type)
        nodo = builder.build(
            node_id=node_id,
            nivel=0,
            es_nodo_objetivo=True
        )
        total_nodos += 1
        
        # Si depth=self, retornar sin buscar padres
        if depth_strategy.is_self_only():
            return nodo, total_nodos
        
        # Buscar ancestros
        root, niveles_subidos = self._build_ancestors(
            child_nodo=nodo,
            child_type=node_type,
            depth_strategy=depth_strategy
        )
        
        # Ajustar niveles después de construir ancestros
        if root != nodo:
            self._adjust_levels(root, niveles_subidos)
            total_nodos += niveles_subidos
        
        return root, total_nodos
    
    def _build_both(
        self,
        node_type: str,
        node_id,
        depth_strategy: DepthStrategy
    ) -> tuple:
        """
        Construye el árbol en ambas direcciones.
        El nodo solicitado queda en el CENTRO.
        """
        total_nodos = 0
        
        # 1. Construir hacia arriba (ancestros)
        if not self.registry.is_root(node_type):
            # Construir ancestros primero
            root, niveles_subidos = self._build_up_from_child(
                child_type=node_type,
                child_id=node_id,
                depth_strategy=depth_strategy
            )
            total_nodos += niveles_subidos + 1  # +1 por el nodo objetivo
            
            # El nodo objetivo ya está incluido en root como descendiente
            # Solo falta expandir sus hijos si depth lo permite
            if not depth_strategy.is_self_only():
                nodo_objetivo = self._find_target_node(root, node_type, node_id)
                if nodo_objetivo and depth_strategy.should_continue(nodo_objetivo.nivel):
                    children_types = self.registry.get_children_types(node_type)
                    for child_type in children_types:
                        child_nodes = self._build_children_from_node(
                            parent_nodo=nodo_objetivo,
                            child_type=child_type,
                            depth_strategy=depth_strategy,
                            parent_level=nodo_objetivo.nivel
                        )
                        nodo_objetivo.hijos.extend(child_nodes)
                        total_nodos += len(child_nodes)
        else:
            # Es raíz, construir hacia abajo normalmente
            root, total_nodos = self._build_down(
                node_type=node_type,
                node_id=node_id,
                depth_strategy=depth_strategy,
                es_nodo_objetivo=True
            )
        
        return root, total_nodos
        
    def _build_children(
        self,
        parent_nodo: TreeNode,
        child_type: str,
        depth_strategy: DepthStrategy,
        nivel_actual: int,
        context: BuildContext = None  # ← NUEVO
    ) -> list:
        """
        Construye los hijos de un nodo padre.
        Busca en el modelo padre los IDs de los hijos.
        """
        children = []
        child_builder = self.registry.get_builder(child_type)
        child_ids = self._get_child_ids(parent_nodo, child_type)
        
        for child_id in child_ids:
            try:
                child_nodo = child_builder.build(
                    node_id=child_id,
                    nivel=nivel_actual + 1,
                    es_nodo_objetivo=False,
                    build_context=context  # ← NUEVO
                )
                children.append(child_nodo)
                
                if depth_strategy.should_continue(nivel_actual + 1):
                    grandchildren_types = self.registry.get_children_types(child_type)
                    # Crear sub-contexto para nietos
                    grandchild_context = context.increment_level() if context else None
                    for grandchild_type in grandchildren_types:
                        grandchild_nodes = self._build_children(
                            parent_nodo=child_nodo,
                            child_type=grandchild_type,
                            depth_strategy=depth_strategy,
                            nivel_actual=nivel_actual + 1,
                            context=grandchild_context  # ← NUEVO
                        )
                        child_nodo.hijos.extend(grandchild_nodes)
            except (ValueError, Exception):
                continue
        
        return children


    # def _build_children(
    #     self,
    #     parent_nodo: TreeNode,
    #     child_type: str,
    #     depth_strategy: DepthStrategy,
    #     nivel_actual: int
    # ) -> list:
    #     """
    #     Construye los hijos de un nodo padre.
    #     Busca en el modelo padre los IDs de los hijos.
    #     """
    #     children = []
    #     child_builder = self.registry.get_builder(child_type)
        
    #     # Obtener IDs de hijos desde el nodo padre
    #     child_ids = self._get_child_ids(parent_nodo, child_type)
        
    #     for child_id in child_ids:
    #         try:
    #             child_nodo = child_builder.build(
    #                 node_id=child_id,
    #                 nivel=nivel_actual + 1,
    #                 es_nodo_objetivo=False
    #             )
    #             children.append(child_nodo)
                
    #             # Expandir recursivamente si depth lo permite
    #             if depth_strategy.should_continue(nivel_actual + 1):
    #                 grandchildren_types = self.registry.get_children_types(child_type)
    #                 for grandchild_type in grandchildren_types:
    #                     grandchild_nodes = self._build_children(
    #                         parent_nodo=child_nodo,
    #                         child_type=grandchild_type,
    #                         depth_strategy=depth_strategy,
    #                         nivel_actual=nivel_actual + 1
    #                     )
    #                     child_nodo.hijos.extend(grandchild_nodes)
                        
    #         except (ValueError, Exception):
    #             continue
        
    #     return children
    
    def _build_children_from_node(
        self,
        parent_nodo: TreeNode,
        child_type: str,
        depth_strategy: DepthStrategy,
        parent_level: int
    ) -> list:
        """Construye hijos desde un nodo ya existente (usado en _build_both)"""
        return self._build_children(
            parent_nodo=parent_nodo,
            child_type=child_type,
            depth_strategy=depth_strategy,
            nivel_actual=parent_level
        )
    
    def _build_ancestors(
        self,
        child_nodo: TreeNode,
        child_type: str,
        depth_strategy: DepthStrategy
    ) -> tuple:
        """
        Construye ancestros recursivamente hacia arriba.
        Retorna (nodo_raiz, niveles_subidos)
        """
        parent_type = self.registry.get_parent_type(child_type)
        
        # Caso base: no hay padre
        if parent_type is None:
            return child_nodo, 0
        
        # Verificar profundidad
        if not depth_strategy.should_continue(0):
            return child_nodo, 0
        
        # Obtener ID del padre desde el nodo hijo
        parent_id = self._get_parent_id(child_nodo, child_type, parent_type)
        
        if parent_id is None:
            return child_nodo, 0
        
        # Construir padre
        parent_builder = self.registry.get_builder(parent_type)
        parent_nodo = parent_builder.build(
            node_id=parent_id,
            nivel=0,  # Nivel temporal
            es_nodo_objetivo=False
        )
        
        # Agregar hijo al padre
        parent_nodo.hijos.append(child_nodo)
        
        # Continuar hacia arriba recursivamente
        root, niveles = self._build_ancestors(
            child_nodo=parent_nodo,
            child_type=parent_type,
            depth_strategy=depth_strategy
        )
        
        return root, niveles + 1
    
    def _build_up_from_child(
        self,
        child_type: str,
        child_id,
        depth_strategy: DepthStrategy
    ) -> tuple:
        """
        Construye hacia arriba desde un hijo (usado en _build_both).
        """
        # Construir nodo objetivo
        builder = self.registry.get_builder(child_type)
        nodo_objetivo = builder.build(
            node_id=child_id,
            nivel=0,
            es_nodo_objetivo=True
        )
        
        # Construir ancestros
        root, niveles = self._build_ancestors(
            child_nodo=nodo_objetivo,
            child_type=child_type,
            depth_strategy=depth_strategy
        )
        
        return root, niveles
    
    def _get_child_ids(self, parent_nodo: TreeNode, child_type: str) -> list:
        """
        Obtiene los IDs de los hijos desde el nodo padre.
        Usa el builder para hacer la consulta inversa.
        """
        child_builder = self.registry.get_builder(child_type)
        
        # Delegar al builder la obtención de IDs hijos
        if hasattr(child_builder, 'get_ids_by_parent'):
            return child_builder.get_ids_by_parent(parent_nodo.id, parent_nodo.tipo_nodo)
        
        return []
    
    def _get_parent_id(self, child_nodo: TreeNode, child_type: str, parent_type: str) -> Optional[int]:
        """
        Obtiene el ID del padre desde el nodo hijo.
        Usa el builder para hacer la consulta.
        """
        child_builder = self.registry.get_builder(child_type)
        
        # Delegar al builder la obtención del ID padre
        if hasattr(child_builder, 'get_parent_id'):
            return child_builder.get_parent_id(child_nodo.id, parent_type)
        
        return None
    
    def _find_target_node(self, root: TreeNode, target_type: str, target_id) -> Optional[TreeNode]:
        """Busca recursivamente el nodo objetivo en el árbol"""
        if root.tipo_nodo == target_type and root.id == target_id:
            return root
        
        for hijo in root.hijos:
            found = self._find_target_node(hijo, target_type, target_id)
            if found:
                return found
        
        return None
    
    def _adjust_levels(self, nodo: TreeNode, offset: int):
        """Ajusta los niveles de un subárbol"""
        nodo.nivel += offset
        for hijo in nodo.hijos:
            self._adjust_levels(hijo, offset)
    
    def _calculate_max_depth(self, nodo: Optional[TreeNode]) -> int:
        """Calcula la profundidad máxima alcanzada en el árbol"""
        if nodo is None:
            return 0
        if not nodo.hijos:
            return nodo.nivel
        return max(self._calculate_max_depth(hijo) for hijo in nodo.hijos)
# spme/spme_presupuesto/services/presupuesto_tree/orchestrator.py
from typing import Union, Optional
from spme_presupuesto.services.presupuesto_tree.dto import TreeNode, TreeMetadata, TreeResponse, BuildContext
from spme_presupuesto.services.presupuesto_tree.registry import PresupuestoRegistry
from spme_presupuesto.services.presupuesto_tree.depth_strategy import DepthStrategy
from spme_presupuesto.services.presupuesto_tree.enums import NodeType, Direction
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudViaje,
    SolicitudReembolso,
    SolicitudPagoDirecto,
    RendicionCuentas,
)
from spme_actividades.models import Actividad, TareaActividad
from collections import defaultdict

class PresupuestoOrchestrator:

    def __init__(self, registry: PresupuestoRegistry):
        self.registry = registry
        self.depth_strategy = DepthStrategy()
        self._total_nodos = 0

    def build_tree(
        self,
        nodo: str,
        id: int,
        depth: Union[str, int] = 'all',
        direction: str = 'down'
    ) -> TreeResponse:
        self._total_nodos = 0
        build_context = BuildContext()

        #comprobacion - si el tipo de nodo existe en el registro
        if nodo not in self.registry.get_registered_types():
            raise ValueError(f"Tipo de nodo '{nodo}' no registrado")

        #Precargar formulario si el nodo inicial es proyecto
        # if nodo == NodeType.PROYECTO.value:
        #     self._precargar_formularios(id, build_context)

        # Precargar formularios si el contexto lo requiere
        if nodo == NodeType.PROYECTO.value:
            self._precargar_formularios(id, build_context)
        elif nodo == NodeType.ACTIVIDAD.value:
            # Cargar formularios de una actividad específica
            self._precargar_formularios_actividad(id, build_context)
        elif nodo == NodeType.TAREA.value:
            # Cargar formularios de una tarea específica
            self._precargar_formularios_tarea(id, build_context)

        if direction == Direction.DOWN.value:
            arbol = self._build_down(nodo, id, depth, build_context)
        elif direction == Direction.UP.value:
            arbol = self._build_up(nodo, id, depth, build_context)
        elif direction == Direction.BOTH.value:
            arbol = self._build_both(nodo, id, depth, build_context)
        else:
            raise ValueError(f"Dirección inválida: {direction}")

        metadata = self._build_metadata(nodo, id, depth, direction, arbol)
        return TreeResponse(arbol=arbol, metadata=metadata)

    # def _build_down(self, nodo, id, depth, build_context, nivel=0):
    #     builder = self.registry.get_builder(nodo)
    #     es_objetivo = (nivel == 0)
    #     current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
    #     self._total_nodos += 1

    #     if self.depth_strategy.can_expand(nivel, depth):
    #         children_types = self.registry.get_children_types(nodo)
    #         for child_type in children_types:
    #             child_builder = self.registry.get_builder(child_type)
    #             child_ids = child_builder.get_ids_by_parent(id, nodo)
    #             for child_id in child_ids:
    #                 child_node = self._build_down(child_type, child_id, depth, build_context, nivel + 1)
    #                 current.hijos.append(child_node)

    #     return current

    def _build_up(self, nodo, id, depth, build_context, nivel=0):
        builder = self.registry.get_builder(nodo)
        es_objetivo = (nivel == 0)
        current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
        self._total_nodos += 1

        if self.depth_strategy.can_expand(nivel, depth):
            parent_type = self.registry.get_parent_type(nodo)
            if parent_type:
                parent_builder = self.registry.get_builder(parent_type)
                parent_id = builder.get_parent_id(id, parent_type)
                if parent_id:
                    parent_node = self._build_up(parent_type, parent_id, depth, build_context, nivel + 1)
                    parent_node.hijos.append(current)
                    return parent_node

        return current

    def _build_both(self, nodo, id, depth, build_context):
        arbol = self._build_up(nodo, id, depth, build_context, nivel=0)
        nodo_objetivo = self._find_objetivo(arbol)
        if nodo_objetivo and self.depth_strategy.can_expand(0, depth):
            children_types = self.registry.get_children_types(nodo)
            for child_type in children_types:
                child_builder = self.registry.get_builder(child_type)
                child_ids = child_builder.get_ids_by_parent(id, nodo)
                for child_id in child_ids:
                    child_node = self._build_down(child_type, child_id, depth, build_context, nivel=1)
                    nodo_objetivo.hijos.append(child_node)
        return arbol

    def _find_objetivo(self, nodo):
        if nodo.es_nodo_objetivo:
            return nodo
        for hijo in nodo.hijos:
            result = self._find_objetivo(hijo)
            if result:
                return result
        return None

    def _find_proyecto(self, nodo: TreeNode) -> Optional[TreeNode]:
        """Busca el nodo proyecto en el árbol."""
        if nodo.tipo_nodo == NodeType.PROYECTO.value:
            return nodo
        for hijo in nodo.hijos:
            result = self._find_proyecto(hijo)
            if result:
                return result
        return None

    def _build_metadata(
    self,
    nodo: str,
    id: int,
    depth,
    direction: str,
    arbol: TreeNode
) -> TreeMetadata:
        """Construye la metadata de la respuesta con info de inclusión/exclusión."""
        profundidad_alcanzada = self._calculate_max_depth(arbol)
        
        # Información de actividades
        actividades_info = self._obtener_info_actividades(nodo, id, arbol)
        
        return TreeMetadata(
            nodo_inicio=f"{nodo}:{id}",
            profundidad_solicitada=depth,
            profundidad_alcanzada=profundidad_alcanzada,
            total_nodos=self._total_nodos,
            direccion=direction,
            estructura=self.registry.get_estructura_texto(),
            actividades=actividades_info
        )

    def _obtener_info_actividades(self, nodo: str, id: int, arbol: TreeNode) -> dict:
        """
        Obtiene información sobre actividades incluidas y excluidas.
        Solo aplica cuando el árbol incluye un proyecto.
        """
        # Buscar el proyecto en el árbol
        proyecto_nodo = self._find_proyecto(arbol)
        
        if not proyecto_nodo or not proyecto_nodo.id:
            return {
                'criterio_exclusion': "estado='CRD' O estaInactiva=true"
            }
        
        try:
            from spme_actividades.models import Actividad
            
            proyecto_id = proyecto_nodo.id
            
            # Total de actividades del proyecto
            total_actividades = Actividad.objects.filter(proyecto_id=proyecto_id).count()
            
            # Actividades excluidas por estado CRD
            excluidas_estado = list(
                Actividad.objects
                .filter(proyecto_id=proyecto_id, estado='CRD')
                .values_list('id', flat=True)
            )
            
            # Actividades excluidas por inactivas
            excluidas_inactivas = list(
                Actividad.objects
                .filter(proyecto_id=proyecto_id, estaInactiva=True)
                .exclude(id__in=excluidas_estado)
                .values_list('id', flat=True)
            )
            
            # Actividades incluidas (las que están en el árbol)
            incluidas = []
            for hijo in proyecto_nodo.hijos:
                if hijo.tipo_nodo == NodeType.ACTIVIDAD.value:
                    incluidas.append(hijo.id)
            
            total_excluidas = len(excluidas_estado) + len(excluidas_inactivas)
            
            return {
                'total_proyecto': total_actividades,
                'incluidas': len(incluidas),
                'excluidas': total_excluidas,
                'excluidas_estado_crd': excluidas_estado,
                'excluidas_inactivas': excluidas_inactivas,
                'criterio_exclusion': "estado='CRD' O estaInactiva=true",
                'ids_incluidas': incluidas
            }
            
        except Exception:
            return {
                'criterio_exclusion': "estado='CRD' O estaInactiva=true"
            }
        

    def _calculate_max_depth(self, nodo, current_depth=0):
        if not nodo.hijos:
            return current_depth
        return max(self._calculate_max_depth(hijo, current_depth + 1) for hijo in nodo.hijos)

    def _build_down(self, nodo, id, depth, build_context, nivel=0):
        builder = self.registry.get_builder(nodo)
        es_objetivo = (nivel == 0)
        current = builder.build(id, build_context, es_nodo_objetivo=es_objetivo, nivel=nivel)
        self._total_nodos += 1

        if self.depth_strategy.can_expand(nivel, depth):
            children_types = self.registry.get_children_types(nodo)
            for child_type in children_types:
                child_builder = self.registry.get_builder(child_type)
                child_ids = child_builder.get_ids_by_parent(id, nodo)
                for child_id in child_ids:
                    child_node = self._build_down(child_type, child_id, depth, build_context, nivel + 1)
                    current.hijos.append(child_node)

        # Después de construir hijos, actualizar nodos virtuales
        if nodo == NodeType.PROYECTO.value:
            self._actualizar_resultados(current)

        return current

    
    #Metodo para la precarga de formulario
    def _precargar_formularios(self, proyecto_id: int, build_context: BuildContext):
        """
        Precarga todos los formularios del proyecto.
        Indexa por actividad_id y tarea_id en el BuildContext.
        """
        # Obtener actividades incluidas
        actividades_ids = list(
            Actividad.objects
            .filter(proyecto_id=proyecto_id, estaInactiva=False)
            .exclude(estado='CRD')
            .values_list('id', flat=True)
        )
        build_context.actividades_incluidas = actividades_ids

        if not actividades_ids:
            return

        # Obtener tareas de esas actividades
        tareas_ids = list(
            TareaActividad.objects
            .filter(actividad_id__in=actividades_ids)
            .values_list('id', flat=True)
        )

        # Inicializar índices
        form_por_actividad = defaultdict(list)
        form_por_tarea = defaultdict(list)

        # Función helper para procesar formularios
        def procesar_formularios(queryset, tipo, campo_monto):
            for form in queryset:
                estado = self._calcular_estado_consolidado(form)
                item = {
                    'id': form.id,
                    'uid': f"{tipo}:{form.id}", 
                    'tipo': tipo,
                    'codigo': form.numeroFormulario or f'{tipo[:3].upper()}-{form.id}',
                    'monto': float(getattr(form, campo_monto) or 0),
                    'estado': estado,
                    'fecha': form.fechaSolicitud.isoformat() if hasattr(form, 'fechaSolicitud') and form.fechaSolicitud else None,
                    'moneda': 'BOB'
                }
                
                # Clasificar según tenga tarea o no
                if form.tarea_id:
                    # Es de tarea: SOLO a tarea, NO a actividad
                    form_por_tarea[form.tarea_id].append(item)
                elif form.actividad_id:
                    # Es de actividad (sin tarea)
                    form_por_actividad[form.actividad_id].append(item)

        # Cargar formularios de actividades
        # Cargar formularios de actividades (solo los que NO tienen tarea)
        procesar_formularios(
            SolicitudFondos.objects.filter(actividad_id__in=actividades_ids, tarea_id__isnull=True),
            'solicitud_fondos', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudReembolso.objects.filter(actividad_id__in=actividades_ids, tarea_id__isnull=True),
            'solicitud_reembolso', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudViaje.objects.filter(actividad_id__in=actividades_ids, tarea_id__isnull=True),
            'solicitud_viaje', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudPagoDirecto.objects.filter(actividad_id__in=actividades_ids, tarea_id__isnull=True),
            'solicitud_pago_directo', 'montoSolicitado'
        )
        procesar_formularios(
            RendicionCuentas.objects.filter(actividad_id__in=actividades_ids, tarea_id__isnull=True),
            'rendicion_cuentas', 'montoDescargado'
        )
        # Cargar formularios de tareas
        procesar_formularios(
            SolicitudFondos.objects.filter(tarea_id__in=tareas_ids),
            'solicitud_fondos', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudReembolso.objects.filter(tarea_id__in=tareas_ids),
            'solicitud_reembolso', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudViaje.objects.filter(tarea_id__in=tareas_ids),
            'solicitud_viaje', 'montoSolicitado'
        )
        procesar_formularios(
            SolicitudPagoDirecto.objects.filter(tarea_id__in=tareas_ids),
            'solicitud_pago_directo', 'montoSolicitado'
        )
        procesar_formularios(
            RendicionCuentas.objects.filter(tarea_id__in=tareas_ids),
            'rendicion_cuentas', 'montoDescargado'
        )

        build_context.formularios_por_actividad = dict(form_por_actividad)
        build_context.formularios_por_tarea = dict(form_por_tarea)

    #Calculo del estado consolidado
    def _calcular_estado_consolidado(self, formulario) -> str:
        """
        Calcula el estado consolidado de un formulario basado en sus validaciones.
        - sin_revisores: no tiene validaciones (BORRADOR - no cuenta para ejecutado)
        - pendiente: al menos un validador no ha votado
        - aprobado: todos aprobaron
        - rechazado: al menos uno rechazó
        """
        if hasattr(formulario, 'validaciones'):
            validaciones = formulario.validaciones.all()
            if not validaciones:
                return 'borrador'
            
            estados = [v.estado for v in validaciones]
            
            if 'RECHAZADO' in estados:
                return 'rechazado'
            if 'PENDIENTE' in estados:
                return 'pendiente'
            if all(e == 'APROBADO' for e in estados):
                return 'aprobado'
            return 'pendiente'
        
        return 'borrador'

    #Actualiza los nodos virtuales con totales y formularios consolidados
    def _actualizar_resultados(self, proyecto_nodo: TreeNode):
        """Actualiza los nodos virtuales con totales calculados y formularios consolidados."""
        actividades = []
        todas_tareas = []
        
        for hijo in proyecto_nodo.hijos:
            if hijo.tipo_nodo == NodeType.ACTIVIDAD.value:
                actividades.append(hijo)
                # ← AGREGAR ESTO:
                suma_presupuesto_tareas = sum(
                    t.datos.get('presupuesto_tarea', 0) for t in hijo.hijos
                )
                suma_ejecutado_tareas = sum(
                    t.datos.get('presupuesto_ejecutado', 0) for t in hijo.hijos
                )
                hijo.datos['presupuesto_tareas'] = suma_presupuesto_tareas
                hijo.datos['ejecutado_tareas'] = suma_ejecutado_tareas
                hijo.datos['cantidad_tareas'] = len(hijo.hijos)
                # ← FIN AGREGAR
                for nieto in hijo.hijos:
                    if nieto.tipo_nodo == NodeType.TAREA.value:
                        todas_tareas.append(nieto)
        
        for hijo in proyecto_nodo.hijos:
            if hijo.tipo_nodo == NodeType.RESULTADO_ACTIVIDADES.value:
                # Totales numéricos
                total_presupuesto = sum(a.datos.get('presupuesto_actividad', 0) for a in actividades)
                total_ejecutado = sum(a.datos.get('presupuesto_ejecutado', 0) for a in actividades)
                
                hijo.datos['presupuesto_total'] = total_presupuesto
                hijo.datos['ejecutado_total'] = total_ejecutado
                hijo.datos['porcentaje_ejecucion_global'] = round(
                    (total_ejecutado / total_presupuesto * 100), 1
                ) if total_presupuesto > 0 else 0.0
                hijo.datos['cantidad_actividades'] = len(actividades)
                
                # Consolidar formularios
                hijo.formularios = self._consolidar_formularios(actividades)
            
            if hijo.tipo_nodo == NodeType.RESULTADO_TAREAS.value:
                # Totales numéricos
                total_presupuesto_tareas = sum(t.datos.get('presupuesto_tarea', 0) for t in todas_tareas)
                total_ejecutado_tareas = sum(t.datos.get('presupuesto_ejecutado', 0) for t in todas_tareas)
                
                hijo.datos['presupuesto_total_tareas'] = total_presupuesto_tareas
                hijo.datos['ejecutado_total_tareas'] = total_ejecutado_tareas
                hijo.datos['porcentaje_ejecucion_tareas'] = round(
                    (total_ejecutado_tareas / total_presupuesto_tareas * 100), 1
                ) if total_presupuesto_tareas > 0 else 0.0
                hijo.datos['cantidad_tareas'] = len(todas_tareas)
                
                # Consolidar formularios
                hijo.formularios = self._consolidar_formularios(todas_tareas)

    def _consolidar_formularios(self, nodos: list) -> list:
        """
        Consolida formularios de múltiples nodos agrupando por tipo.
        Retorna lista con totales por tipo y un total consolidado.
        """
        from collections import defaultdict
        
        # Agrupar por tipo
        por_tipo = defaultdict(lambda: {
            'cantidad': 0,
            'monto_total': 0.0,
            'monto_aprobado': 0.0,
            'monto_pendiente': 0.0,
            'monto_rechazado': 0.0,
            'monto_borrador': 0.0
        })
        
        for nodo in nodos:
            for form in nodo.formularios:
                tipo = form['tipo']
                monto = form['monto']
                estado = form['estado']
                
                por_tipo[tipo]['cantidad'] += 1
                por_tipo[tipo]['monto_total'] += monto
                
                if estado == 'aprobado':
                    por_tipo[tipo]['monto_aprobado'] += monto
                elif estado == 'pendiente':
                    por_tipo[tipo]['monto_pendiente'] += monto
                elif estado == 'rechazado':
                    por_tipo[tipo]['monto_rechazado'] += monto
                elif estado == 'borrador':
                    por_tipo[tipo]['monto_borrador'] += monto
        
        # Construir resultado
        resultado = []
        total_general = {
            'cantidad': 0,
            'monto_total': 0.0,
            'monto_aprobado': 0.0,
            'monto_pendiente': 0.0,
            'monto_rechazado': 0.0,
            'monto_borrador': 0.0
        }
        
        for tipo, datos in sorted(por_tipo.items()):
            resultado.append({
                'tipo': tipo,
                **datos
            })
            for k in total_general:
                if k != 'tipo':
                    total_general[k] += datos[k]
        
        # Agregar total consolidado al inicio
        resultado.insert(0, {
            'tipo': 'total_consolidado',
            **total_general
        })
        
        return resultado
    

    def _precargar_formularios_actividad(self, actividad_id, build_context):
        """Carga formularios de una actividad específica."""
        from collections import defaultdict
        form_por_actividad = defaultdict(list)
        
        def procesar(queryset, tipo, campo_monto):
            for form in queryset:
                estado = self._calcular_estado_consolidado(form)
                form_por_actividad[form.actividad_id].append({
                    'id': form.id,
                    'uid': f"{tipo}:{form.id}",
                    'tipo': tipo,
                    'codigo': form.numeroFormulario or f'{tipo[:3].upper()}-{form.id}',
                    'monto': float(getattr(form, campo_monto) or 0),
                    'estado': estado,
                    'fecha': form.fechaSolicitud.isoformat() if hasattr(form, 'fechaSolicitud') and form.fechaSolicitud else None,
                    'moneda': 'BOB'
                })
        
        procesar(SolicitudFondos.objects.filter(actividad_id=actividad_id, tarea_id__isnull=True), 'solicitud_fondos', 'montoSolicitado')
        procesar(SolicitudReembolso.objects.filter(actividad_id=actividad_id, tarea_id__isnull=True), 'solicitud_reembolso', 'montoSolicitado')
        procesar(SolicitudViaje.objects.filter(actividad_id=actividad_id, tarea_id__isnull=True), 'solicitud_viaje', 'montoSolicitado')
        procesar(SolicitudPagoDirecto.objects.filter(actividad_id=actividad_id, tarea_id__isnull=True), 'solicitud_pago_directo', 'montoSolicitado')
        procesar(RendicionCuentas.objects.filter(actividad_id=actividad_id, tarea_id__isnull=True), 'rendicion_cuentas', 'montoDescargado')
        
        build_context.formularios_por_actividad = dict(form_por_actividad)
        build_context.actividades_incluidas = [actividad_id]


    def _precargar_formularios_tarea(self, tarea_id, build_context):
        """Carga formularios de una tarea específica."""
        from collections import defaultdict
        form_por_tarea = defaultdict(list)
        
        def procesar(queryset, tipo, campo_monto):
            for form in queryset:
                estado = self._calcular_estado_consolidado(form)
                form_por_tarea[form.tarea_id].append({
                    'id': form.id,
                    'uid': f"{tipo}:{form.id}",
                    'tipo': tipo,
                    'codigo': form.numeroFormulario or f'{tipo[:3].upper()}-{form.id}',
                    'monto': float(getattr(form, campo_monto) or 0),
                    'estado': estado,
                    'fecha': form.fechaSolicitud.isoformat() if hasattr(form, 'fechaSolicitud') and form.fechaSolicitud else None,
                    'moneda': 'BOB'
                })
        
        procesar(SolicitudFondos.objects.filter(tarea_id=tarea_id), 'solicitud_fondos', 'montoSolicitado')
        procesar(SolicitudReembolso.objects.filter(tarea_id=tarea_id), 'solicitud_reembolso', 'montoSolicitado')
        procesar(SolicitudViaje.objects.filter(tarea_id=tarea_id), 'solicitud_viaje', 'montoSolicitado')
        procesar(SolicitudPagoDirecto.objects.filter(tarea_id=tarea_id), 'solicitud_pago_directo', 'montoSolicitado')
        procesar(RendicionCuentas.objects.filter(tarea_id=tarea_id), 'rendicion_cuentas', 'montoDescargado')
        
        build_context.formularios_por_tarea = dict(form_por_tarea)
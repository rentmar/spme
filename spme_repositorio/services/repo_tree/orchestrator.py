# spme/spme_repositorio/services/repo_tree/orchestrator.py
import logging
from typing import Optional, List, Dict, Any

from .enums import RepoNodeType
from .dto import RepoTreeNode, RepoTreeResponse
from .registry import RepoNodeRegistry
from .builders import (
    ProyectoRepoBuilder,
    ObjetivoGeneralRepoBuilder,
    IndicadorOGRepoBuilder,
    ResultadoOGRepoBuilder,
    IndicadorROGRepoBuilder,
    ObjetivoEspecificoRepoBuilder,
    IndicadorOERepoBuilder,
    ResultadoOERepoBuilder,
    IndicadorROERepoBuilder,
    ActividadRepoBuilder,
    TareaRepoBuilder,
    SolicitudFondosActRepoBuilder,
    SolicitudFondosTareaRepoBuilder,
    SolicitudReembolsoActRepoBuilder,
    SolicitudReembolsoTareaRepoBuilder,
    SolicitudViajeActRepoBuilder,
    SolicitudViajeTareaRepoBuilder,
    SolicitudPagoDirectoActRepoBuilder,
    SolicitudPagoDirectoTareaRepoBuilder,
    RendicionCuentasActRepoBuilder,
    RendicionCuentasTareaRepoBuilder,
    InformeActividadRepoBuilder,
    InformeTareaRepoBuilder,
    ProductoOERepoBuilder,
    ProductoROERepoBuilder,
)

logger = logging.getLogger(__name__)


class RepoTreeOrchestrator:
    """Orquestador del árbol de repositorio."""

    CONTENEDOR_LABELS = {
        RepoNodeType.INDICADOR_OG.value: 'Indicadores de Objetivo General',
        RepoNodeType.RESULTADO_OG.value: 'Resultados de Objetivo General',
        RepoNodeType.INDICADOR_ROG.value: 'Indicadores de Resultado',
        RepoNodeType.OBJETIVO_ESPECIFICO_OG.value: 'Objetivos Específicos',
        RepoNodeType.INDICADOR_OE.value: 'Indicadores de Objetivo Específico',
        RepoNodeType.RESULTADO_OE.value: 'Resultados de Objetivo Específico',
        RepoNodeType.INDICADOR_ROE.value: 'Indicadores de Resultado',
        RepoNodeType.ACTIVIDAD.value: 'Actividades',
        RepoNodeType.SOLICITUD_FONDOS_ACT.value: 'Solicitudes de Fondos',
        RepoNodeType.SOLICITUD_FONDOS_TAREA.value: 'Solicitudes de Fondos',
        RepoNodeType.SOLICITUD_REEMBOLSO_ACT.value: 'Solicitudes de Reembolso',
        RepoNodeType.SOLICITUD_REEMBOLSO_TAREA.value: 'Solicitudes de Reembolso',
        RepoNodeType.SOLICITUD_VIAJE_ACT.value: 'Solicitudes de Viaje',
        RepoNodeType.SOLICITUD_VIAJE_TAREA.value: 'Solicitudes de Viaje',
        RepoNodeType.SOLICITUD_PAGO_DIRECTO_ACT.value: 'Solicitudes de Pago Directo',
        RepoNodeType.SOLICITUD_PAGO_DIRECTO_TAREA.value: 'Solicitudes de Pago Directo',
        RepoNodeType.RENDICION_CUENTAS_ACT.value: 'Rendiciones',
        RepoNodeType.RENDICION_CUENTAS_TAREA.value: 'Rendiciones',
        RepoNodeType.INFORME_ACTIVIDAD.value: 'Informes',
        RepoNodeType.INFORME_TAREA.value: 'Informes',
        RepoNodeType.TAREA.value: 'Tareas',
        RepoNodeType.PRODUCTO_OE.value: 'Productos de Objetivo Específico',
        RepoNodeType.PRODUCTO_ROE.value: 'Productos de Resultado de Objetivo Especifico',
    }

    TIPOS_CON_CONTENEDOR = [
        RepoNodeType.INDICADOR_OG.value,
        RepoNodeType.RESULTADO_OG.value,
        RepoNodeType.INDICADOR_ROG.value,
        RepoNodeType.OBJETIVO_ESPECIFICO_OG.value,
        RepoNodeType.INDICADOR_OE.value,
        RepoNodeType.RESULTADO_OE.value,
        RepoNodeType.INDICADOR_ROE.value,
        RepoNodeType.ACTIVIDAD.value,
        RepoNodeType.SOLICITUD_FONDOS_ACT.value,
        RepoNodeType.SOLICITUD_FONDOS_TAREA.value,
        RepoNodeType.SOLICITUD_REEMBOLSO_ACT.value,
        RepoNodeType.SOLICITUD_REEMBOLSO_TAREA.value,
        RepoNodeType.SOLICITUD_VIAJE_ACT.value,
        RepoNodeType.SOLICITUD_VIAJE_TAREA.value,
        RepoNodeType.SOLICITUD_PAGO_DIRECTO_ACT.value,
        RepoNodeType.SOLICITUD_PAGO_DIRECTO_TAREA.value,
        RepoNodeType.RENDICION_CUENTAS_ACT.value,
        RepoNodeType.RENDICION_CUENTAS_TAREA.value,
        RepoNodeType.INFORME_ACTIVIDAD.value,
        RepoNodeType.INFORME_TAREA.value,
        RepoNodeType.TAREA.value,
        RepoNodeType.PRODUCTO_OE.value,
        RepoNodeType.PRODUCTO_ROE.value,
    ]

    def __init__(self):
        self.registry = RepoNodeRegistry()
        self._register_builders()

    def _register_builders(self):
        builders = [
            ProyectoRepoBuilder(self.registry),
            ObjetivoGeneralRepoBuilder(self.registry),
            IndicadorOGRepoBuilder(self.registry),
            ResultadoOGRepoBuilder(self.registry),
            IndicadorROGRepoBuilder(self.registry),
            ObjetivoEspecificoRepoBuilder(self.registry),
            IndicadorOERepoBuilder(self.registry),
            ResultadoOERepoBuilder(self.registry),
            IndicadorROERepoBuilder(self.registry),
            ActividadRepoBuilder(self.registry),
            TareaRepoBuilder(self.registry),
            SolicitudFondosActRepoBuilder(self.registry),
            SolicitudFondosTareaRepoBuilder(self.registry),
            SolicitudReembolsoActRepoBuilder(self.registry),
            SolicitudReembolsoTareaRepoBuilder(self.registry),
            SolicitudViajeActRepoBuilder(self.registry),
            SolicitudViajeTareaRepoBuilder(self.registry),
            SolicitudPagoDirectoActRepoBuilder(self.registry),
            SolicitudPagoDirectoTareaRepoBuilder(self.registry),
            RendicionCuentasActRepoBuilder(self.registry),
            RendicionCuentasTareaRepoBuilder(self.registry),
            InformeActividadRepoBuilder(self.registry),
            InformeTareaRepoBuilder(self.registry),
            ProductoOERepoBuilder(self.registry),
            ProductoROERepoBuilder(self.registry),
        ]

        for builder in builders:
            self.registry.register_builder(builder.get_node_type(), builder)

    def build_tree(self, proyecto_id: int) -> RepoTreeResponse:
        proyecto_builder = self.registry.get_builder(RepoNodeType.PROYECTO.value)
        if not proyecto_builder:
            raise ValueError(f"No hay builder registrado para '{RepoNodeType.PROYECTO.value}'")

        proyecto_nodo = proyecto_builder.build(proyecto_id)
        proyecto_nodo.children = self._build_children(
            nodo_id=proyecto_id,
            nodo_tipo=RepoNodeType.PROYECTO.value,
        )

        from spme_estructuracion_proyecto.models import Proyecto
        proyecto = Proyecto.objects.get(id=proyecto_id)

        return RepoTreeResponse(
            proyecto_id=proyecto_id,
            proyecto_nombre=proyecto.titulo,
            tree=[proyecto_nodo],
        )

    def _build_children(self, nodo_id: int, nodo_tipo: str) -> List[RepoTreeNode]:
        children_types = self.registry.get_children_types(nodo_tipo)
        if not children_types:
            return []

        children = []

        for child_type in children_types:
            child_builder = self.registry.get_builder(child_type)
            if not child_builder:
                continue

            try:
                child_ids = child_builder.get_ids_by_parent(
                    parent_id=nodo_id,
                    parent_type=nodo_tipo,
                )
            except Exception as e:
                logger.error(f"Error obteniendo hijos de {nodo_tipo}->{child_type}: {e}")
                continue

            child_nodes = []
            for child_id in child_ids:
                try:
                    child_nodo = child_builder.build(child_id)
                    child_children = self._build_children(
                        nodo_id=child_id,
                        nodo_tipo=child_type,
                    )
                    repo_children = child_nodo.children
                    child_nodo.children = repo_children + child_children
                    child_nodes.append(child_nodo)
                except Exception as e:
                    logger.error(f"Error construyendo {child_type} {child_id}: {e}")
                    continue

            if child_type in self.TIPOS_CON_CONTENEDOR:
                contenedor = self._build_contenedor(
                    nodo_padre_id=f"{nodo_tipo}-{nodo_id}",
                    child_type=child_type,
                    children=child_nodes,
                )
                children.append(contenedor)
            else:
                children.extend(child_nodes)

        return children

    def _build_contenedor(self, nodo_padre_id: str, child_type: str, children: List[RepoTreeNode]) -> RepoTreeNode:
        label = self.CONTENEDOR_LABELS.get(child_type, child_type)
        contenedor_id = f"{nodo_padre_id}-contenedor-{child_type}"
        cantidad = len(children)
        titulo = f"{label} ({cantidad})" if cantidad > 0 else label

        return RepoTreeNode(
            id=contenedor_id,
            title=titulo,
            nodo_tipo=RepoNodeType.CONTENEDOR.value,
            children=children,
        )

    def build_node(self, nodo_id: int, nodo_tipo: str) -> Optional[RepoTreeNode]:
        builder = self.registry.get_builder(nodo_tipo)
        if not builder:
            raise ValueError(f"No hay builder registrado para '{nodo_tipo}'")
        return builder.build(nodo_id)

    def build_subtree(self, nodo_id: int, nodo_tipo: str) -> Optional[RepoTreeNode]:
        builder = self.registry.get_builder(nodo_tipo)
        if not builder:
            raise ValueError(f"No hay builder registrado para '{nodo_tipo}'")
        nodo = builder.build(nodo_id)
        nodo.children = self._build_children(nodo_id=nodo_id, nodo_tipo=nodo_tipo)
        return nodo

    def build_node_with_parent(self, nodo_id: int, nodo_tipo: str) -> Optional[RepoTreeNode]:
        parent_type = self.registry.get_parent_type(nodo_tipo)
        if not parent_type:
            return self.build_node(nodo_id, nodo_tipo)

        parent_builder = self.registry.get_builder(parent_type)
        child_builder = self.registry.get_builder(nodo_tipo)
        if not parent_builder or not child_builder:
            raise ValueError(f"No hay builder registrado para '{parent_type}' o '{nodo_tipo}'")

        parent_id = child_builder.get_parent_id(nodo_id, parent_type)
        if parent_id is None:
            return None

        parent_nodo = parent_builder.build(parent_id)
        child_nodo = self.build_node(nodo_id, nodo_tipo)
        parent_nodo.children = [child_nodo]
        return parent_nodo

    def build_node_with_parent_and_siblings(self, nodo_id: int, nodo_tipo: str) -> Optional[RepoTreeNode]:
        parent_type = self.registry.get_parent_type(nodo_tipo)
        if not parent_type:
            return self.build_node(nodo_id, nodo_tipo)

        parent_builder = self.registry.get_builder(parent_type)
        child_builder = self.registry.get_builder(nodo_tipo)
        if not parent_builder or not child_builder:
            raise ValueError(f"No hay builder registrado para '{parent_type}' o '{nodo_tipo}'")

        parent_id = child_builder.get_parent_id(nodo_id, parent_type)
        if parent_id is None:
            return None

        parent_nodo = parent_builder.build(parent_id)
        parent_nodo.children = self._build_children(nodo_id=parent_id, nodo_tipo=parent_type)
        return parent_nodo
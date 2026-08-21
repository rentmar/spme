# spme/spme_repositorio/services/repo_tree/registry.py
from typing import Optional, List, Dict, Any
from django.apps import apps

from .enums import RepoNodeType


class RepoNodeRegistry:
    """Registro centralizado de la estructura del árbol de repositorio."""

    def __init__(self):
        self._structure: Dict[str, Dict[str, Any]] = {}
        self._builders: Dict[str, Any] = {}
        self._initialize_structure()

    def _initialize_structure(self):
        """Define la estructura jerárquica y modelos del árbol de repositorio."""
        self._structure = {
            # ============================================================
            # ESTRUCTURA
            # ============================================================
            RepoNodeType.PROYECTO.value: {
                'children': [
                    RepoNodeType.OBJETIVO_GENERAL.value,
                    RepoNodeType.ACTIVIDAD.value,
                ],
                'parent': None,
                'label': 'Proyecto',
                'model': 'Proyecto',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': None,
                'acceso_repositorio': False,
            },
            RepoNodeType.OBJETIVO_GENERAL.value: {
                'children': [
                    RepoNodeType.INDICADOR_OG.value,
                    RepoNodeType.RESULTADO_OG.value,
                    RepoNodeType.OBJETIVO_ESPECIFICO_OG.value,
                ],
                'parent': RepoNodeType.PROYECTO.value,
                'label': 'Objetivo General',
                'model': 'ObjetivoGeneralProyecto',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'proyecto_id',
                'acceso_repositorio': False,
            },
            RepoNodeType.INDICADOR_OG.value: {
                'children': [],
                'parent': RepoNodeType.OBJETIVO_GENERAL.value,
                'label': 'Indicador OG',
                'model': 'IndicadorObjetivoGeneral',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_general_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.RESULTADO_OG.value: {
                'children': [
                    RepoNodeType.INDICADOR_ROG.value,
                ],
                'parent': RepoNodeType.OBJETIVO_GENERAL.value,
                'label': 'Resultado OG',
                'model': 'ResultadoOG',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_general_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.INDICADOR_ROG.value: {
                'children': [],
                'parent': RepoNodeType.RESULTADO_OG.value,
                'label': 'Indicador ROG',
                'model': 'IndicadorResultadoObjGral',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'resultado_og_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.OBJETIVO_ESPECIFICO_OG.value: {
                'children': [
                    RepoNodeType.INDICADOR_OE.value,
                    RepoNodeType.RESULTADO_OE.value,
                    RepoNodeType.PRODUCTO_OE.value,
                ],
                'parent': RepoNodeType.OBJETIVO_GENERAL.value,
                'label': 'Objetivo Específico',
                'model': 'ObjetivoEspecificoProyecto',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_general_id',
                'acceso_repositorio': False,
            },
            RepoNodeType.INDICADOR_OE.value: {
                'children': [],
                'parent': RepoNodeType.OBJETIVO_ESPECIFICO_OG.value,
                'label': 'Indicador OE',
                'model': 'IndicadorObjetivoEspecifico',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_especifico_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.RESULTADO_OE.value: {
                'children': [
                    RepoNodeType.INDICADOR_ROE.value,
                    RepoNodeType.PRODUCTO_ROE.value,
                ],
                'parent': RepoNodeType.OBJETIVO_ESPECIFICO_OG.value,
                'label': 'Resultado OE',
                'model': 'ResultadoOE',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_especifico_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.INDICADOR_ROE.value: {
                'children': [],
                'parent': RepoNodeType.RESULTADO_OE.value,
                'label': 'Indicador ROE',
                'model': 'IndicadorResultadoObjEspecifico',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'resultado_obj_especifico_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.PRODUCTO_OE.value: {
                'children': [],
                'parent': RepoNodeType.OBJETIVO_ESPECIFICO_OG.value,
                'label': 'Producto OE',
                'model': 'ProductoOE',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'objetivo_especifico_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.PRODUCTO_ROE.value: {
                'children': [],
                'parent': RepoNodeType.RESULTADO_OE.value,
                'label': 'Producto ROE',
                'model': 'ProductoResultadoOE',
                'app': 'spme_estructuracion_proyecto',
                'fk_field': 'resultado_oe_id',
                'acceso_repositorio': True,
            },

            # ============================================================
            # ACTIVIDAD Y JERARQUÍA
            # ============================================================
            RepoNodeType.ACTIVIDAD.value: {
                'children': [
                    RepoNodeType.SOLICITUD_FONDOS_ACT.value,
                    RepoNodeType.SOLICITUD_REEMBOLSO_ACT.value,
                    RepoNodeType.SOLICITUD_VIAJE_ACT.value,
                    RepoNodeType.SOLICITUD_PAGO_DIRECTO_ACT.value,
                    RepoNodeType.RENDICION_CUENTAS_ACT.value,
                    RepoNodeType.INFORME_ACTIVIDAD.value,
                    RepoNodeType.TAREA.value,
                ],
                'parent': RepoNodeType.PROYECTO.value,
                'label': 'Actividad',
                'model': 'Actividad',
                'app': 'spme_actividades',
                'fk_field': 'proyecto_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.TAREA.value: {
                'children': [
                    RepoNodeType.SOLICITUD_FONDOS_TAREA.value,
                    RepoNodeType.SOLICITUD_REEMBOLSO_TAREA.value,
                    RepoNodeType.SOLICITUD_VIAJE_TAREA.value,
                    RepoNodeType.SOLICITUD_PAGO_DIRECTO_TAREA.value,
                    RepoNodeType.RENDICION_CUENTAS_TAREA.value,
                    RepoNodeType.INFORME_TAREA.value,
                ],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Tarea',
                'model': 'TareaActividad',
                'app': 'spme_actividades',
                'fk_field': 'actividad_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_FONDOS_ACT.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Solicitud de Fondos',
                'model': 'SolicitudFondos',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'filter_extra': {'tarea__isnull': True},
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_FONDOS_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Solicitud de Fondos',
                'model': 'SolicitudFondos',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_REEMBOLSO_ACT.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Solicitud de Reembolso',
                'model': 'SolicitudReembolso',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'filter_extra': {'tarea__isnull': True},
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_REEMBOLSO_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Solicitud de Reembolso',
                'model': 'SolicitudReembolso',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_VIAJE_ACT.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Solicitud de Viaje',
                'model': 'SolicitudViaje',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'filter_extra': {'tarea__isnull': True},
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_VIAJE_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Solicitud de Viaje',
                'model': 'SolicitudViaje',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_PAGO_DIRECTO_ACT.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Solicitud de Pago Directo',
                'model': 'SolicitudPagoDirecto',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'filter_extra': {'tarea__isnull': True},
                'acceso_repositorio': True,
            },
            RepoNodeType.SOLICITUD_PAGO_DIRECTO_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Solicitud de Pago Directo',
                'model': 'SolicitudPagoDirecto',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.RENDICION_CUENTAS_ACT.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Rendición de Cuentas',
                'model': 'RendicionCuentas',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'filter_extra': {'tarea__isnull': True},
                'acceso_repositorio': True,
            },
            RepoNodeType.RENDICION_CUENTAS_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Rendición de Cuentas',
                'model': 'RendicionCuentas',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.INFORME_ACTIVIDAD.value: {
                'children': [],
                'parent': RepoNodeType.ACTIVIDAD.value,
                'label': 'Informe de Actividad',
                'model': 'InformeActividadPrincipal',
                'app': 'spme_monitoreo',
                'fk_field': 'actividad_id',
                'acceso_repositorio': True,
            },
            RepoNodeType.INFORME_TAREA.value: {
                'children': [],
                'parent': RepoNodeType.TAREA.value,
                'label': 'Informe de Tarea',
                'model': 'InformeTareaPrincipal',
                'app': 'spme_monitoreo',
                'fk_field': 'tarea_id',
                'acceso_repositorio': True,
            },
        }

    # ================================================================
    # MÉTODOS DE CONSULTA
    # ================================================================

    def get_children_types(self, nodo_tipo: str) -> List[str]:
        config = self._structure.get(nodo_tipo)
        return config.get('children', []) if config else []

    def get_parent_type(self, nodo_tipo: str) -> Optional[str]:
        config = self._structure.get(nodo_tipo)
        return config.get('parent') if config else None

    def get_model(self, nodo_tipo: str):
        config = self._structure.get(nodo_tipo)
        if not config:
            return None
        app_label = config.get('app')
        model_name = config.get('model')
        if not app_label or not model_name:
            return None
        return apps.get_model(app_label, model_name)

    def get_fk_field(self, nodo_tipo: str) -> Optional[str]:
        config = self._structure.get(nodo_tipo)
        return config.get('fk_field') if config else None

    def get_filter_extra(self, nodo_tipo: str) -> Optional[Dict[str, Any]]:
        config = self._structure.get(nodo_tipo)
        return config.get('filter_extra') if config else None

    def get_label(self, nodo_tipo: str) -> str:
        config = self._structure.get(nodo_tipo)
        return config.get('label', nodo_tipo) if config else nodo_tipo

    def get_acceso_repositorio(self, nodo_tipo: str) -> bool:
        """Retorna si el nodo tiene acceso al repositorio."""
        config = self._structure.get(nodo_tipo)
        return config.get('acceso_repositorio', False) if config else False

    def get_registered_types(self) -> List[str]:
        return list(self._structure.keys())

    def register_builder(self, nodo_tipo: str, builder: Any):
        self._builders[nodo_tipo] = builder

    def get_builder(self, nodo_tipo: str):
        return self._builders.get(nodo_tipo)

    def is_registered(self, nodo_tipo: str) -> bool:
        return nodo_tipo in self._structure
# spme_presupuesto/repositories/presupuesto_tree_v3_repository.py
# spme_presupuesto/repositories/presupuesto_tree_v3_repository.py

from typing import Optional, List, Dict, Any
from spme_validaciones.services.consolidacion.service import ConsolidacionValidacionService


class PresupuestoTreeV3Repository:
    """
    Repositorio para obtener datos del árbol presupuestario V3
    integrado con ConsolidacionValidacionService.
    """

    def __init__(self):
        self.consolidacion_service = ConsolidacionValidacionService()

    # ============================================================
    # MÉTODOS PARA PROYECTO
    # ============================================================

    def obtener_proyecto(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        from spme_estructuracion_proyecto.models import Proyecto

        proyecto = Proyecto.objects.filter(id=proyecto_id).first()
        if not proyecto:
            return None

        return {
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'nombre': proyecto.titulo,  # Estandarizado a 'nombre'
            'titulo': proyecto.titulo,
            'descripcion': proyecto.descripcion or '',
            'estado': proyecto.estado,
            'estado_display': proyecto.get_estado_display(),
            'presupuesto': float(proyecto.presupuesto or 0),
            'fecha_inicio': str(proyecto.fecha_inicio) if proyecto.fecha_inicio else None,
            'fecha_finalizacion': str(proyecto.fecha_finalizacion) if proyecto.fecha_finalizacion else None,
            'moneda': 'BOB',
            'desglose_financiadores': self._obtener_desglose_proyecto(proyecto),
        }

    def obtener_actividades_proyecto(self, proyecto_id: int) -> List[int]:
        from spme_actividades.models import Actividad

        actividades = Actividad.objects.filter(
            proyecto_id=proyecto_id,
            estaInactiva=False,
        ).exclude(
            estado='CRD'
        ).values_list('id', flat=True)

        return list(actividades)

    # ============================================================
    # MÉTODOS PARA ACTIVIDAD
    # ============================================================

    def obtener_actividad(self, actividad_id: int) -> Optional[Dict[str, Any]]:
        from spme_actividades.models import Actividad

        actividad = Actividad.objects.filter(id=actividad_id).first()
        if not actividad:
            return None

        return {
            'id': actividad.id,
            'codigo': actividad.codigo,
            'nombre': actividad.nombreCorto or '',
            'descripcion': actividad.descripcion or '',
            'estado': actividad.estado,
            'estado_display': actividad.get_estado_display(),
            'presupuesto': float(actividad.presupuesto or 0),
            'fecha_inicio': str(actividad.fecha_inicio) if actividad.fecha_inicio else None,
            'fecha_cierre': str(actividad.fecha_cierre) if actividad.fecha_cierre else None,
            'responsable': self._obtener_nombre_responsable(actividad),
            'moneda': 'BOB',
            'desglose_financiadores': self._obtener_desglose_actividad(actividad),
        }

    def obtener_tareas_actividad(self, actividad_id: int) -> List[int]:
        from spme_actividades.models import TareaActividad

        tareas = TareaActividad.objects.filter(
            actividad_id=actividad_id,
        ).values_list('id', flat=True)

        return list(tareas)

    def obtener_proyecto_de_actividad(self, actividad_id: int) -> Optional[int]:
        from spme_actividades.models import Actividad

        actividad = Actividad.objects.filter(id=actividad_id).first()
        return actividad.proyecto_id if actividad else None

    # ============================================================
    # MÉTODOS PARA TAREA
    # ============================================================

    def obtener_tarea(self, tarea_id: int) -> Optional[Dict[str, Any]]:
        from spme_actividades.models import TareaActividad

        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        if not tarea:
            return None

        return {
            'id': tarea.id,
            'codigo': tarea.codigo,
            'nombre': tarea.titulo or '',  # Estandarizado a 'nombre'
            'titulo': tarea.titulo or '',
            'descripcion': tarea.descripcion or '',
            'estado': tarea.estado,
            'estado_display': tarea.get_estado_display(),
            'presupuesto': float(tarea.presupuesto or 0),
            'fecha_creacion': str(tarea.fecha_creacion) if tarea.fecha_creacion else None,
            'fecha_ejecucion': str(tarea.fecha_ejecucion) if tarea.fecha_ejecucion else None,
            'fecha_limite': str(tarea.fecha_limite) if tarea.fecha_limite else None,
            'moneda': 'BOB',
            'desglose_financiadores': self._obtener_desglose_tarea(tarea),
        }

    def obtener_actividad_de_tarea(self, tarea_id: int) -> Optional[int]:
        from spme_actividades.models import TareaActividad

        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        return tarea.actividad_id if tarea else None

    # ============================================================
    # MÉTODOS PARA FORMULARIOS Y DETERMINACIÓN DE ESTADO
    # ============================================================

    def obtener_formularios_tarea(self, tarea_id: int) -> List[Dict[str, Any]]:
        from spme_actividades.models import TareaActividad

        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        if not tarea:
            return []

        actividad_id = tarea.actividad_id
        formularios = []
        formularios.extend(self._obtener_rendiciones_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_reembolsos_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_pagos_directos_tarea(tarea_id, actividad_id))
        return formularios

    def _evaluar_estado_consolidado(self, tipo_solicitud: str, solicitud_id: int, metodo_resolucion: Optional[str] = None) -> str:
        """
        Delega la determinación del estado al servicio ConsolidacionValidacionService.
        """
        try:
            # Si no se especifica un método explícito, se utiliza el por defecto del servicio
            resultado = self.consolidacion_service.consolidar(
                tipo_solicitud=tipo_solicitud,
                solicitud_id=solicitud_id,
                metodo_resolucion=metodo_resolucion or 'UNANIMIDAD'  # O la estrategia por defecto configurada
            )
            # Extraer el valor del estado del objeto de resultado consolidado
            return getattr(resultado, 'estado', 'pendiente').lower()
        except Exception:
            return 'pendiente'

    def _obtener_rendiciones_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import RendicionCuentas

        formularios = []
        rendiciones = RendicionCuentas.objects.filter(tarea_id=tarea_id, actividad_id=actividad_id)
        for r in rendiciones:
            metodo = getattr(r, 'metodoResolucion', None) or getattr(r, 'metodo_resolucion', 'UNANIMIDAD')
            estado = self._evaluar_estado_consolidado('rendicion_cuentas', r.id, metodo)
            formularios.append({
                'id': r.id,
                'uid': f'rendicion_cuentas:{r.id}',
                'tipo': 'rendicion_cuentas',
                'codigo': r.numeroFormulario or f'RC-{r.id}',
                'monto': float(r.montoDescargado or 0),
                'estado': estado,
                'fecha': str(r.fechaRendicion) if r.fechaRendicion else None,
                'moneda': 'BOB',
            })
        return formularios

    def _obtener_reembolsos_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudReembolso

        formularios = []
        reembolsos = SolicitudReembolso.objects.filter(tarea_id=tarea_id, actividad_id=actividad_id)
        for r in reembolsos:
            metodo = getattr(r, 'metodoResolucion', None) or getattr(r, 'metodo_resolucion', 'UNANIMIDAD')
            estado = self._evaluar_estado_consolidado('solicitud_reembolso', r.id, metodo)
            formularios.append({
                'id': r.id,
                'uid': f'solicitud_reembolso:{r.id}',
                'tipo': 'solicitud_reembolso',
                'codigo': r.numeroFormulario or f'SR-{r.id}',
                'monto': float(r.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(r.fechaSolicitud) if r.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        return formularios

    def _obtener_pagos_directos_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudPagoDirecto

        formularios = []
        pagos = SolicitudPagoDirecto.objects.filter(tarea_id=tarea_id, actividad_id=actividad_id)
        for p in pagos:
            metodo = getattr(p, 'metodoResolucion', None) or getattr(p, 'metodo_resolucion', 'UNANIMIDAD')
            estado = self._evaluar_estado_consolidado('solicitud_pago_directo', p.id, metodo)
            formularios.append({
                'id': p.id,
                'uid': f'solicitud_pago_directo:{p.id}',
                'tipo': 'solicitud_pago_directo',
                'codigo': p.numeroFormulario or f'SPD-{p.id}',
                'monto': float(p.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(p.fechaSolicitud) if p.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        return formularios

    # ============================================================
    # AUXILIARES Y DESGLOSE
    # ============================================================

    def _obtener_desglose_proyecto(self, proyecto) -> List[Dict[str, Any]]:
        desglose = []
        for fondos in proyecto.procedencia_fondos.all():
            desglose.append({
                'sigla': fondos.sigla or '',
                'nombre': fondos.financiera or '',
                'monto': 0.0,
            })
        return desglose

    def _obtener_desglose_actividad(self, actividad) -> List[Dict[str, Any]]:
        desglose = []
        if actividad.procedencia_fondos:
            for fondos in actividad.procedencia_fondos:
                desglose.append({
                    'id': fondos.get('id'),
                    'nombre': fondos.get('nombre', ''),
                    'monto': float(fondos.get('monto', 0)),
                    'es_existente': fondos.get('esExistente', True),
                    'tipo': fondos.get('tipo', 'registrado'),
                })
        return desglose

    def _obtener_desglose_tarea(self, tarea) -> List[Dict[str, Any]]:
        desglose = []
        if tarea.presupuestoDesglose:
            for fondos in tarea.presupuestoDesglose:
                desglose.append({
                    'id': fondos.get('id'),
                    'nombre': fondos.get('nombre', ''),
                    'monto': float(fondos.get('monto', 0)),
                    'es_existente': fondos.get('esExistente', False),
                    'tipo': fondos.get('tipo', 'manual'),
                })
        return desglose

    def _obtener_nombre_responsable(self, actividad) -> str:
        if actividad.responsable:
            return actividad.responsable.get_full_name() or actividad.responsable.email
        return ''
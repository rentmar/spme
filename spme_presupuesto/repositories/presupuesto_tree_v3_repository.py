# spme_presupuesto/repositories/presupuesto_tree_v3_repository.py

from typing import Optional, List, Dict, Any


class PresupuestoTreeV3Repository:
    """
    Repositorio para obtener datos del árbol presupuestario V3.
    """
    
    # ============================================================
    # MÉTODOS PARA PROYECTO
    # ============================================================
    
    def obtener_proyecto(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de un proyecto."""
        from spme_estructuracion_proyecto.models import Proyecto
        
        proyecto = Proyecto.objects.filter(id=proyecto_id).first()
        if not proyecto:
            return None
        
        return {
            'id': proyecto.id,
            'codigo': proyecto.codigo,
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
        """Obtiene IDs de actividades válidas de un proyecto."""
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
        """Obtiene los datos de una actividad."""
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
        """Obtiene IDs de tareas de una actividad."""
        from spme_actividades.models import TareaActividad
        
        tareas = TareaActividad.objects.filter(
            actividad_id=actividad_id,
        ).values_list('id', flat=True)
        
        return list(tareas)
    
    def obtener_proyecto_de_actividad(self, actividad_id: int) -> Optional[int]:
        """Obtiene el ID del proyecto padre."""
        from spme_actividades.models import Actividad
        
        actividad = Actividad.objects.filter(id=actividad_id).first()
        if actividad:
            return actividad.proyecto_id
        return None
    
    # ============================================================
    # MÉTODOS PARA TAREA
    # ============================================================
    
    def obtener_tarea(self, tarea_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de una tarea."""
        from spme_actividades.models import TareaActividad
        
        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        if not tarea:
            return None
        
        return {
            'id': tarea.id,
            'codigo': tarea.codigo,
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
        """Obtiene el ID de la actividad padre."""
        from spme_actividades.models import TareaActividad
        
        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        if tarea:
            return tarea.actividad_id
        return None
    
    # ============================================================
    # MÉTODOS PARA FORMULARIOS
    # ============================================================
    
    def obtener_formularios_tarea(self, tarea_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los formularios de una tarea."""
        from spme_actividades.models import TareaActividad
        
        tarea = TareaActividad.objects.filter(id=tarea_id).first()
        if not tarea:
            return []
        
        actividad_id = tarea.actividad_id
        
        formularios = []
        formularios.extend(self._obtener_rendiciones_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_reembolsos_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_solicitudes_fondos_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_solicitudes_viaje_tarea(tarea_id, actividad_id))
        formularios.extend(self._obtener_pagos_directos_tarea(tarea_id, actividad_id))
        
        return formularios
    
    def obtener_formularios_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los formularios directos de una actividad."""
        formularios = []
        formularios.extend(self._obtener_rendiciones_actividad(actividad_id))
        formularios.extend(self._obtener_reembolsos_actividad(actividad_id))
        formularios.extend(self._obtener_solicitudes_fondos_actividad(actividad_id))
        formularios.extend(self._obtener_solicitudes_viaje_actividad(actividad_id))
        formularios.extend(self._obtener_pagos_directos_actividad(actividad_id))
        
        return formularios
    
    # ============================================================
    # MÉTODOS PRIVADOS PARA FORMULARIOS - TAREA
    # ============================================================
    
    def _obtener_rendiciones_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import RendicionCuentas
        
        formularios = []
        rendiciones = RendicionCuentas.objects.filter(
            tarea_id=tarea_id,
            actividad_id=actividad_id,
        )
        
        for rendicion in rendiciones:
            estado = self._determinar_estado_rendicion(rendicion)
            formularios.append({
                'id': rendicion.id,
                'uid': f'rendicion_cuentas:{rendicion.id}',
                'tipo': 'rendicion_cuentas',
                'codigo': rendicion.numeroFormulario or f'RC-{rendicion.id}',
                'monto': float(rendicion.montoDescargado or 0),
                'estado': estado,
                'fecha': str(rendicion.fechaRendicion) if rendicion.fechaRendicion else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_reembolsos_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudReembolso
        
        formularios = []
        reembolsos = SolicitudReembolso.objects.filter(
            tarea_id=tarea_id,
            actividad_id=actividad_id,
        )
        
        for reembolso in reembolsos:
            estado = self._determinar_estado_solicitud(reembolso)
            formularios.append({
                'id': reembolso.id,
                'uid': f'solicitud_reembolso:{reembolso.id}',
                'tipo': 'solicitud_reembolso',
                'codigo': reembolso.numeroFormulario or f'SR-{reembolso.id}',
                'monto': float(reembolso.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(reembolso.fechaSolicitud) if reembolso.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_solicitudes_fondos_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudFondos
        
        formularios = []
        solicitudes = SolicitudFondos.objects.filter(
            tarea_id=tarea_id,
            actividad_id=actividad_id,
        )
        
        for solicitud in solicitudes:
            estado = self._determinar_estado_solicitud(solicitud)
            formularios.append({
                'id': solicitud.id,
                'uid': f'solicitud_fondos:{solicitud.id}',
                'tipo': 'solicitud_fondos',
                'codigo': solicitud.numeroFormulario or f'SF-{solicitud.id}',
                'monto': float(solicitud.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(solicitud.fechaSolicitud) if solicitud.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_solicitudes_viaje_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudViaje
        
        formularios = []
        solicitudes = SolicitudViaje.objects.filter(
            tarea_id=tarea_id,
            actividad_id=actividad_id,
        )
        
        for solicitud in solicitudes:
            estado = self._determinar_estado_solicitud(solicitud)
            formularios.append({
                'id': solicitud.id,
                'uid': f'solicitud_viaje:{solicitud.id}',
                'tipo': 'solicitud_viaje',
                'codigo': solicitud.numeroFormulario or f'SV-{solicitud.id}',
                'monto': float(solicitud.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(solicitud.fechaSolicitud) if solicitud.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_pagos_directos_tarea(self, tarea_id: int, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudPagoDirecto
        
        formularios = []
        pagos = SolicitudPagoDirecto.objects.filter(
            tarea_id=tarea_id,
            actividad_id=actividad_id,
        )
        
        for pago in pagos:
            estado = self._determinar_estado_solicitud(pago)
            formularios.append({
                'id': pago.id,
                'uid': f'solicitud_pago_directo:{pago.id}',
                'tipo': 'solicitud_pago_directo',
                'codigo': pago.numeroFormulario or f'SPD-{pago.id}',
                'monto': float(pago.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(pago.fechaSolicitud) if pago.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    # ============================================================
    # MÉTODOS PRIVADOS PARA FORMULARIOS - ACTIVIDAD
    # ============================================================
    
    def _obtener_rendiciones_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import RendicionCuentas
        
        formularios = []
        rendiciones = RendicionCuentas.objects.filter(
            actividad_id=actividad_id,
            tarea_id__isnull=True,
        )
        
        for rendicion in rendiciones:
            estado = self._determinar_estado_rendicion(rendicion)
            formularios.append({
                'id': rendicion.id,
                'uid': f'rendicion_cuentas:{rendicion.id}',
                'tipo': 'rendicion_cuentas',
                'codigo': rendicion.numeroFormulario or f'RC-{rendicion.id}',
                'monto': float(rendicion.montoDescargado or 0),
                'estado': estado,
                'fecha': str(rendicion.fechaRendicion) if rendicion.fechaRendicion else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_reembolsos_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudReembolso
        
        formularios = []
        reembolsos = SolicitudReembolso.objects.filter(
            actividad_id=actividad_id,
            tarea_id__isnull=True,
        )
        
        for reembolso in reembolsos:
            estado = self._determinar_estado_solicitud(reembolso)
            formularios.append({
                'id': reembolso.id,
                'uid': f'solicitud_reembolso:{reembolso.id}',
                'tipo': 'solicitud_reembolso',
                'codigo': reembolso.numeroFormulario or f'SR-{reembolso.id}',
                'monto': float(reembolso.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(reembolso.fechaSolicitud) if reembolso.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_solicitudes_fondos_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudFondos
        
        formularios = []
        solicitudes = SolicitudFondos.objects.filter(
            actividad_id=actividad_id,
            tarea_id__isnull=True,
        )
        
        for solicitud in solicitudes:
            estado = self._determinar_estado_solicitud(solicitud)
            formularios.append({
                'id': solicitud.id,
                'uid': f'solicitud_fondos:{solicitud.id}',
                'tipo': 'solicitud_fondos',
                'codigo': solicitud.numeroFormulario or f'SF-{solicitud.id}',
                'monto': float(solicitud.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(solicitud.fechaSolicitud) if solicitud.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_solicitudes_viaje_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudViaje
        
        formularios = []
        solicitudes = SolicitudViaje.objects.filter(
            actividad_id=actividad_id,
            tarea_id__isnull=True,
        )
        
        for solicitud in solicitudes:
            estado = self._determinar_estado_solicitud(solicitud)
            formularios.append({
                'id': solicitud.id,
                'uid': f'solicitud_viaje:{solicitud.id}',
                'tipo': 'solicitud_viaje',
                'codigo': solicitud.numeroFormulario or f'SV-{solicitud.id}',
                'monto': float(solicitud.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(solicitud.fechaSolicitud) if solicitud.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    def _obtener_pagos_directos_actividad(self, actividad_id: int) -> List[Dict[str, Any]]:
        from spme_monitoreo.models import SolicitudPagoDirecto
        
        formularios = []
        pagos = SolicitudPagoDirecto.objects.filter(
            actividad_id=actividad_id,
            tarea_id__isnull=True,
        )
        
        for pago in pagos:
            estado = self._determinar_estado_solicitud(pago)
            formularios.append({
                'id': pago.id,
                'uid': f'solicitud_pago_directo:{pago.id}',
                'tipo': 'solicitud_pago_directo',
                'codigo': pago.numeroFormulario or f'SPD-{pago.id}',
                'monto': float(pago.montoSolicitado or 0),
                'estado': estado,
                'fecha': str(pago.fechaSolicitud) if pago.fechaSolicitud else None,
                'moneda': 'BOB',
            })
        
        return formularios
    
    # ============================================================
    # MÉTODOS PARA DETERMINAR ESTADOS
    # ============================================================
    
    def _determinar_estado_solicitud(self, solicitud) -> str:
        validaciones = solicitud.validaciones.all()
        
        if not validaciones:
            return 'pendiente'
        
        estados = [v.estado for v in validaciones]
        
        if 'RECHAZADO' in estados:
            return 'rechazado'
        
        if all(estado == 'APROBADO' for estado in estados):
            return 'aprobado'
        
        return 'pendiente'
    
    def _determinar_estado_rendicion(self, rendicion) -> str:
        validaciones = rendicion.validaciones.all()
        
        if not validaciones:
            return 'pendiente'
        
        estados = [v.estado for v in validaciones]
        
        if 'RECHAZADO' in estados:
            return 'rechazado'
        
        if all(estado == 'APROBADO' for estado in estados):
            return 'aprobado'
        
        return 'pendiente'
    
    # ============================================================
    # MÉTODOS PARA DESGLOSE
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
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def _obtener_nombre_responsable(self, actividad) -> str:
        if actividad.responsable:
            return actividad.responsable.get_full_name() or actividad.responsable.email
        return ''
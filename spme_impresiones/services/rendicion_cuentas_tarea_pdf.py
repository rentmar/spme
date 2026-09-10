# spme_impresiones/pdf_generators/rendicion_cuentas_tarea.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import RendicionCuentas
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService


class RendicionCuentasTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Rendición de Cuentas (exclusivo para Tareas)
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_cuentas_tarea_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        if not isinstance(obj, RendicionCuentas):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentas")
        
        fecha_desembolso = obj.fechaDesembolso.strftime('%d/%m/%Y') if obj.fechaDesembolso else "No especificada"
        fecha_actividad = obj.fechaActividad.strftime('%d/%m/%Y') if obj.fechaActividad else "No especificada"
        fecha_rendicion = obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada"
        
        tarea_data = self._get_tarea_data(obj)
        
        # Determinar tipo de solicitud relacionada
        tipo_solicitud = "No especificada"
        solicitud_numero = "No especificado"
        
        if obj.solicitudFondos:
            tipo_solicitud = "Solicitud de Fondos"
            solicitud_numero = obj.solicitudFondos.numeroFormulario or f"SF-{obj.solicitudFondos.id}"
        elif obj.solicitudReembolso:
            tipo_solicitud = "Solicitud de Reembolso"
            solicitud_numero = obj.solicitudReembolso.numeroFormulario or f"SR-{obj.solicitudReembolso.id}"
        elif obj.solicitudViaje:
            tipo_solicitud = "Solicitud de Viaje"
            solicitud_numero = obj.solicitudViaje.numeroFormulario or f"SV-{obj.solicitudViaje.id}"
        elif obj.solicitudPagoDirecto:
            tipo_solicitud = "Solicitud de Pago Directo"
            solicitud_numero = obj.solicitudPagoDirecto.numeroFormulario or f"SPD-{obj.solicitudPagoDirecto.id}"
        
        # Validadores del servicio
        if self.USAR_ETIQUETAS_GENERICAS:
            validadores = self.validacion_service.obtener_validadores(obj, self.etiquetas_revisor)
        else:
            validadores = self.validacion_service.obtener_validadores(obj)
        
        solicitante = self.validacion_service.obtener_solicitante(obj)
        estado_documento = self.validacion_service.calcular_estado_documento(validadores)
        
        contexto_validacion = {
            'validadores': validadores,
            'solicitante': solicitante,
            'estado_documento': estado_documento,
            'total_validadores': len(validadores),
            'aprobados': sum(1 for v in validadores if v['estado'] == 'APROBADO'),
            'pendientes': sum(1 for v in validadores if v['estado'] == 'PENDIENTE'),
            'rechazados': sum(1 for v in validadores if v['estado'] == 'RECHAZADO'),
        }
        
        # Procesar detalle de fondos
        detalle_fondos, total_calculado = self._procesar_detalle_fondos(obj)
        
        # Cálculos financieros
        monto_asignado = float(obj.montoAsignado) if obj.montoAsignado else 0.0
        monto_descargado = float(obj.montoDescargado) if obj.montoDescargado else 0.0
        saldo = float(obj.saldo) if obj.saldo else (monto_asignado - monto_descargado)
        
        context = {
            'numero_formulario': obj.numeroFormulario or f"RC-{obj.id:04d}",
            'fecha_emision': fecha_rendicion,
            'fecha_rendicion': fecha_rendicion,
            'tipo_documento': 'RENDICIÓN DE CUENTAS - SUBACTIVIDAD',
            'subtipo_documento': 'RC-T',
            'cpte_diario': obj.cpteDiario or "No especificado",
            
            'solicitante': contexto_validacion['solicitante'],
            'tarea': tarea_data,
            
            'fecha_desembolso': fecha_desembolso,
            'fecha_actividad': fecha_actividad,
            'monto_asignado': monto_asignado,
            'monto_descargado': monto_descargado,
            'saldo': saldo,
            'total_calculado': total_calculado,
            'tiene_saldo': saldo > 0,
            'saldo_absoluto': abs(saldo),
            'tiene_saldo_favor': saldo > 0,
            'tiene_saldo_debito': saldo < 0,
            
            'descripcion_actividad': obj.descripcionActividad or "No especificada",
            'lugar_actividad': obj.lugarActividad or "No especificado",
            'lugar_rendicion': obj.lugarRendicion or "No especificado",
            
            'tipo_solicitud': tipo_solicitud,
            'solicitud_numero': solicitud_numero,
            
            'validadores': contexto_validacion['validadores'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            'detalle_fondos': detalle_fondos,
            'tiene_detalle': len(detalle_fondos) > 0,
            'cantidad_items': len(detalle_fondos),
        }
        
        return context
    
    def _get_tarea_data(self, obj):
        if not obj.tarea:
            return {}
        return {
            'codigo': obj.tarea.codigo or "No asignado",
            'titulo': obj.tarea.titulo or "Sin título",
            'fecha_creacion': obj.tarea.fecha_creacion.strftime('%d/%m/%Y') if obj.tarea.fecha_creacion else "No especificada",
            'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if obj.tarea.fecha_limite else "No especificada",
            'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0.0,
        }
    
    def _procesar_detalle_fondos(self, obj):
        detalle_fondos = []
        total_calculado = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_fondos, total_calculado
        
        try:
            items = obj.detalleDestinoFondos if isinstance(obj.detalleDestinoFondos, list) else []
            
            for index, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    continue
                
                fecha_item = item.get('fecha', '')
                if fecha_item:
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                        fecha_item = fecha_obj.strftime('%d/%m/%Y')
                    except: pass
                
                partida = item.get('partida_sf') or item.get('partida') or ''
                
                fuente_raw = (item.get('fuente') or item.get('fuente_financiamiento') or 
                             item.get('fuente_fin') or item.get('origen') or 'No especificada')
                
                if isinstance(fuente_raw, dict):
                    sigla = fuente_raw.get('sigla')
                    financiera = fuente_raw.get('financiera')
                    fuente = sigla + '-' + financiera
                    # fuente = fuente_raw.get('sigla', str(fuente_raw))
                else:
                    fuente = str(fuente_raw)
                
                factura_recibo = item.get('factura_recibo') or item.get('factura') or item.get('recibo') or ''
                descripcion = item.get('descripcion') or item.get('concepto') or item.get('descripcionGasto') or ''
                monto = float(item.get('monto', 0))
                total_calculado += monto
                
                detalle_fondos.append({
                    'numero': index,
                    'fecha': fecha_item,
                    'partida': str(partida),
                    'fuente': fuente,
                    'factura_recibo': str(factura_recibo),
                    'descripcion': str(descripcion),
                    'monto': monto,
                })
        
        except Exception as e:
            print(f"Error procesando detalle de fondos: {e}")
        
        return detalle_fondos, total_calculado
    
    def generate_filename(self, obj):
        numero = obj.numeroFormulario or f"RC-{obj.id:04d}"
        nombre_responsable = "responsable"
        if obj.usuario and obj.usuario.nombre:
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts: nombre_responsable = nombre_parts[0].lower()
        return f"Rendicion_Cuentas_Tarea_{nombre_responsable}_{numero}.pdf"
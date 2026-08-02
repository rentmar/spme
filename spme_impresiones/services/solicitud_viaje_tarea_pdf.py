# spme_impresiones/pdf_generators/solicitud_viaje_tarea.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViaje
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService


class SolicitudViajeTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje (exclusivo para Tareas)
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_tarea_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        if not isinstance(obj, SolicitudViaje):
            raise ValueError("El objeto debe ser una instancia de SolicitudViaje")
        
        # Fechas
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
        fecha_evento = obj.fechaEvento.strftime('%d/%m/%Y') if obj.fechaEvento else "No especificada"
        
        # Datos de la tarea
        tarea_data = self._get_tarea_data(obj)
        
        # Obtener validadores del servicio
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
        
        # Procesar detalle de gastos
        detalle_gastos, total_calculado = self._procesar_detalle_gastos(obj)
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_calculado
        
        # Procesar forma de pago
        datos_transferencia = self._procesar_datos_transferencia(obj)
        
        context = {
            'numero_formulario': obj.numeroFormulario or f"SV-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'fecha_solicitud': fecha_solicitud,
            'tipo_documento': 'SOLICITUD DE VIAJE - TAREA',
            'subtipo_documento': 'SV-T',
            
            # Solicitante (desde el servicio)
            'solicitante': contexto_validacion['solicitante'],
            
            # Tarea
            'tarea': tarea_data,
            
            # Información del evento/viaje
            'evento': obj.evento or "No especificado",
            'lugar_evento': obj.lugarEvento or "No especificado",
            'fecha_evento': fecha_evento,
            'instituciones_participantes': obj.institucionesParticipantes or "No especificado",
            'organizador': obj.organizador or "No especificado",
            'quien_cubre_gastos': obj.quienCubreGastos or "No especificado",
            'justificacion_asistencia': obj.justificacionAsistencia or "No especificado",
            'fondos_unitas': obj.fondosUnitas or "No especificado",
            'tareas_previas': obj.tareasPrevias or "No especificado",
            
            # Datos de solicitud
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'monto_solicitado': monto_solicitado,
            
            # Validaciones
            'validadores': contexto_validacion['validadores'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            # Forma de pago
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'datos_transferencia': datos_transferencia,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'total_calculado': total_calculado,
            'tiene_detalle': len(detalle_gastos) > 0,
            'cantidad_items': len(detalle_gastos),
        }
        
        return context
    
    def _get_tarea_data(self, obj):
        if not obj.tarea:
            return {}
        
        return {
            'codigo': obj.tarea.codigo or "No asignado",
            'titulo': obj.tarea.titulo or "Sin título",
            'descripcion': obj.tarea.descripcion or "Sin descripción",
            'fecha_creacion': obj.tarea.fecha_creacion.strftime('%d/%m/%Y') if obj.tarea.fecha_creacion else "No especificada",
            'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if obj.tarea.fecha_limite else "No especificada",
            'estado': obj.tarea.get_estado_display() if hasattr(obj.tarea, 'get_estado_display') else "No especificado",
            'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0.0,
        }
    
    def _procesar_datos_transferencia(self, obj):
        datos_forma_pago = {
            'efectivo': {},
            'transferencia': {},
            'cheque': {},
            'otros': {},
            'mostrar_efectivo': False,
            'mostrar_transferencia': False,
            'mostrar_cheque': False,
            'mostrar_otros': False,
            'tipo': None,
        }
        
        if not obj.datos_forma_pago:
            return datos_forma_pago
        
        try:
            if isinstance(obj.datos_forma_pago, dict):
                datos_forma_pago.update(obj.datos_forma_pago)
            elif isinstance(obj.datos_forma_pago, str):
                import json
                try:
                    parsed_data = json.loads(obj.datos_forma_pago)
                    datos_forma_pago.update(parsed_data)
                except json.JSONDecodeError:
                    pass
            
            codigo = obj.formaPago.codigo if obj.formaPago else None
            
            mapeo_tipos = {
                'EFEC': 'efectivo',
                'TB': 'transferencia',
                'CHE': 'cheque',
            }
            
            tipo_seleccionado = mapeo_tipos.get(codigo)
            
            if tipo_seleccionado:
                datos_forma_pago['tipo'] = tipo_seleccionado
                datos_forma_pago[f'mostrar_{tipo_seleccionado}'] = True
        
        except Exception as e:
            print(f"Error procesando datos de forma de pago: {e}")
        
        return datos_forma_pago
    
    def _procesar_detalle_gastos(self, obj):
        detalle_gastos = []
        total_calculado = 0.0
        
        if not obj.detalleGasto:
            return detalle_gastos, total_calculado
        
        try:
            data_dict = obj.detalleGasto
            
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except:
                    return detalle_gastos, total_calculado
            
            items = []
            if isinstance(data_dict, dict) and 'items' in data_dict:
                items = data_dict['items']
            elif isinstance(data_dict, list):
                items = data_dict
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                fecha_item = item.get('fecha', '')
                if fecha_item:
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                        fecha_item = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                partida = item.get('partida_sf') or item.get('partida') or item.get('codigo') or ''
                
                fuente_raw = (
                    item.get('fuente') or 
                    item.get('fuente_financiamiento') or 
                    item.get('fuente_fin') or 
                    item.get('origen') or 
                    'No especificada'
                )
                
                if isinstance(fuente_raw, dict):
                    fuente = fuente_raw.get('sigla', str(fuente_raw))
                else:
                    fuente = str(fuente_raw)
                
                monto = float(item.get('monto', 0))
                total_calculado += monto
                
                detalle_gastos.append({
                    'fecha': fecha_item,
                    'partida': str(partida),
                    'fuente': fuente,
                    'descripcion': item.get('descripcion', '') or item.get('concepto', ''),
                    'factura_recibo': item.get('factura_recibo', ''),
                    'monto': monto,
                })
                
        except Exception as e:
            print(f"Error procesando detalle de gastos: {e}")
        
        return detalle_gastos, total_calculado
    
    def generate_filename(self, obj):
        numero = obj.numeroFormulario or f"SV-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        return f"Solicitud_Viaje_Tarea_{nombre_solicitante}_{numero}.pdf"
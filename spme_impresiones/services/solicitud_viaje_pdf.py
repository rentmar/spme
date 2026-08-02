# spme_impresiones/pdf_generators/solicitud_viaje.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViaje
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService


class SolicitudViajePDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real (Contable, Coordinador, etc.)
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_template.html'
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
        
        # Procesar detalle de gastos
        detalle_gastos, total_gastos = self._procesar_detalle_gastos(obj)
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos
        
        # Obtener validadores según configuración
        if self.USAR_ETIQUETAS_GENERICAS:
            validadores = self.validacion_service.obtener_validadores(obj, self.etiquetas_revisor)
        else:
            validadores = self.validacion_service.obtener_validadores(obj)
        
        solicitante = self.validacion_service.obtener_solicitante(obj)
        estado = self.validacion_service.calcular_estado_documento(validadores)
        
        contexto_validacion = {
            'validadores': validadores,
            'solicitante': solicitante,
            'estado_documento': estado,
            'total_validadores': len(validadores),
            'aprobados': sum(1 for v in validadores if v['estado'] == 'APROBADO'),
            'pendientes': sum(1 for v in validadores if v['estado'] == 'PENDIENTE'),
            'rechazados': sum(1 for v in validadores if v['estado'] == 'RECHAZADO'),
        }
        
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"SV-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            
            # Información del solicitante (desde el servicio)
            'nombre_solicitante': contexto_validacion['solicitante']['nombre'],
            'documento_identidad': contexto_validacion['solicitante']['documento_identidad'],
            'cargo': contexto_validacion['solicitante']['cargo'],
            
            # Información del viaje
            'evento': obj.evento or "No especificado",
            'lugar_evento': obj.lugarEvento or "No especificado",
            'fecha_evento': obj.fechaEvento.strftime('%d/%m/%Y') if obj.fechaEvento else "No especificada",
            'instituciones_participantes': obj.institucionesParticipantes or "No especificado",
            'organizador': obj.organizador or "No especificado",
            
            # Justificación y fondos
            'quien_cubre_gastos': obj.quienCubreGastos or "No especificado",
            'justificacion_asistencia': obj.justificacionAsistencia or "No especificado",
            'fondos_unitas': obj.fondosUnitas or "No especificado",
            'tareas_previas': obj.tareasPrevias or "No especificado",
            
            # Información de pago
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'monto_solicitado': monto_solicitado,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'total_gastos': total_gastos,
            
            # Validaciones (NUEVO - desde el servicio)
            'validadores': contexto_validacion['validadores'],
            'solicitante': contexto_validacion['solicitante'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            # Información de actividad
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE VIAJE',
            'subtipo_documento': 'F-03',
        }
        
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        
        return context
    
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
        total_gastos = 0.0
        
        if not obj.detalleGasto:
            return detalle_gastos, total_gastos
        
        try:
            data_dict = obj.detalleGasto
            
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    return detalle_gastos, total_gastos
            
            items_list = []
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items_list = data_dict['items']
                elif 'gastos' in data_dict:
                    items_list = data_dict['gastos']
                elif 'detalle' in data_dict:
                    items_list = data_dict['detalle']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            if not items_list:
                return detalle_gastos, total_gastos
            
            for index, item in enumerate(items_list):
                if not isinstance(item, dict):
                    continue
                
                partida = item.get('partida', '')
                
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
                
                concepto = item.get('concepto') or item.get('descripcion') or f"Item {index + 1}"
                
                monto_raw = item.get('monto', 0)
                try:
                    monto = float(monto_raw)
                    total_gastos += monto
                except (ValueError, TypeError):
                    monto = 0.0
                
                detalle_gastos.append({
                    'indice': index + 1,
                    'partida': partida,
                    'fuente': fuente,
                    'concepto': concepto,
                    'monto': monto,
                })
            
        except Exception as e:
            print(f"Error procesando detalle de gastos de viaje: {e}")
        
        return detalle_gastos, total_gastos
    
    def generate_filename(self, obj):
        numero = obj.numeroFormulario or f"SV{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Viaje_{numero_limpio}.pdf"
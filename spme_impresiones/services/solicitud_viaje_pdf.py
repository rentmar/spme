from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViaje

class SolicitudViajePDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Viaje
        """
        if not isinstance(obj, SolicitudViaje):
            raise ValueError("El objeto debe ser una instancia de SolicitudViaje")
        
        # Obtener datos del solicitante
        nombre_solicitante = "No asignado"
        documento_identidad = "No asignado"
        cargo = "No asignado"
        
        if obj.usuario:
            nombre_solicitante = f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip()
            documento_identidad = obj.usuario.ci or "No asignado"
            cargo = obj.usuario.cargo or "No asignado"
        
        # Procesar detalle de gastos
        detalle_gastos = []
        total_gastos = 0.0
        monto_solicitado = 0.0
        
        # Procesar detalleGasto
        if obj.detalleGasto:
            detalle_gastos, total_gastos = self._procesar_detalle_gastos(obj)
            # Usar el total calculado o el monto del objeto
            monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos
        else:
            monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else 0.0
        
        # Obtener datos de responsables
        nombre_responsable = "No asignado"
        if obj.responsable:
            nombre_responsable = f"{obj.responsable.nombre or ''} {obj.responsable.paterno or ''}".strip()
        
        nombre_coordinador = "No asignado"
        if obj.coordinador:
            nombre_coordinador = f"{obj.coordinador.nombre or ''} {obj.coordinador.paterno or ''}".strip()
        
        # Construir contexto
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"SV-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            
            # Información del solicitante
            'nombre_solicitante': nombre_solicitante,
            'documento_identidad': documento_identidad,
            'cargo': cargo,
            
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
            
            # Información de validaciones
            'nombre_responsable': nombre_responsable,
            'nombre_coordinador': nombre_coordinador,
            
            # Información de actividad si existe
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE VIAJE',
            'subtipo_documento': 'F-03',
        }
        
        # Procesar datos de transferencia (igual que en fondos)
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        
        # DEBUG: Imprimir para verificar
        print(f"[DEBUG] Detalle gastos: {detalle_gastos}")
        print(f"[DEBUG] Total gastos: {total_gastos}")
        print(f"[DEBUG] Monto solicitado: {monto_solicitado}")
        
        return context
    
    def _procesar_datos_transferencia(self, obj):
        """
        Procesa los datos de forma de pago del formulario (IGUAL QUE EN FONDOS)
        """
        datos_forma_pago = {
            'tipo': 'otros',
            'otros': {},
            'transferencia': {},
            'mostrar_transferencia': False,
            'mostrar_otros': False,
            'mostrar_efectivo': False,
        }
        
        if not obj.datos_forma_pago:
            return datos_forma_pago
        
        try:
            if isinstance(obj.datos_forma_pago, dict):
                datos_forma_pago.update(obj.datos_forma_pago)
                
                # Determinar qué tipo de pago mostrar
                tiene_datos_otros = datos_forma_pago.get('otros', {}).get('nombre_otros')
                tiene_datos_transferencia = datos_forma_pago.get('transferencia', {}).get('nombre_transferencia')
                
                # Verificar por el tipo de forma de pago
                if obj.formaPago:
                    if 'transferencia' in obj.formaPago.formaPago.lower():
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = False
                    elif 'cheque' in obj.formaPago.formaPago.lower():
                        datos_forma_pago['tipo'] = 'otros'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = True
                        datos_forma_pago['mostrar_efectivo'] = False
                    else:  # Efectivo u otros
                        datos_forma_pago['tipo'] = 'efectivo'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = True
                else:
                    if tiene_datos_transferencia:
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                    elif tiene_datos_otros:
                        datos_forma_pago['tipo'] = 'otros'
                        datos_forma_pago['mostrar_otros'] = True
            
            elif isinstance(obj.datos_forma_pago, str):
                import json
                try:
                    parsed_data = json.loads(obj.datos_forma_pago)
                    datos_forma_pago.update(parsed_data)
                except json.JSONDecodeError:
                    pass
        
        except Exception as e:
            print(f"Error procesando datos de forma de pago: {e}")
        
        return datos_forma_pago
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del viaje
        Formato esperado: {"items": [{"partida": "...", "fuente": "...", "concepto": "...", "monto": ...}]}
        """
        detalle_gastos = []
        total_gastos = 0.0
        
        if not obj.detalleGasto:
            return detalle_gastos, total_gastos
        
        try:
            # Obtener los datos
            data_dict = obj.detalleGasto
            
            # Si es string, parsear JSON
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    print(f"[ERROR] No se pudo parsear JSON: {data_dict[:100]}")
                    return detalle_gastos, total_gastos
            
            print(f"[DEBUG] data_dict: {data_dict}")
            
            # Extraer items
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
            
            print(f"[DEBUG] items_list: {items_list}")
            
            if not items_list:
                return detalle_gastos, total_gastos
            
            # Procesar cada item
            for index, item in enumerate(items_list):
                if not isinstance(item, dict):
                    continue
                
                print(f"[DEBUG] Procesando item {index}: {item}")
                
                # Extraer campos - según tu JSON
                partida = item.get('partida', '')
                
                #Fuente de finaciamiento
                fuente = (
                    item.get('fuente') or 
                    item.get('fuente_financiamiento') or 
                    item.get('fuente_fin') or 
                    item.get('origen') or 
                    'No especificada'
                )      
                concepto = item.get('concepto') or item.get('descripcion') or f"Item {index + 1}"
                
                # Extraer monto
                monto_raw = item.get('monto', 0)
                try:
                    monto = float(monto_raw)
                    total_gastos += monto
                except (ValueError, TypeError):
                    monto = 0.0
                
                # Agregar a la lista
                detalle_gastos.append({
                    'indice': index + 1,
                    'partida': partida,
                    'fuente': fuente,
                    'concepto': concepto,
                    'monto': monto,
                })
            
            print(f"[DEBUG] detalle_gastos final: {detalle_gastos}")
            print(f"[DEBUG] total_gastos final: {total_gastos}")
            
        except Exception as e:
            print(f"Error procesando detalle de gastos de viaje: {e}")
            import traceback
            traceback.print_exc()
        
        return detalle_gastos, total_gastos
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        numero = obj.numeroFormulario or f"SV{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Viaje_{numero_limpio}.pdf"
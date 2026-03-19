# services/solicitud_reembolso_act_pei_pdf.py
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudReembolsoActPei
from spme_estructuracion_pei.models import ActividadPei
import json
from datetime import datetime

class SolicitudReembolsoActPeiPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Reembolso de Actividad PEI
    Para solicitudes que NO tienen tarea asociada (solo actividad)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_reembolso_act_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para SolicitudReembolsoActPei sin tarea
        """
        if not isinstance(obj, SolicitudReembolsoActPei):
            raise ValueError("El objeto debe ser una instancia de SolicitudReembolsoActPei")
        
        # Validar que sea actividad (sin tarea)
        if obj.tarea:
            raise ValueError("Este generador es solo para solicitudes de actividad")
        
        # Obtener datos del solicitante directamente
        nombre_solicitante = "No asignado"
        documento_identidad = "No asignado"
        cargo = "No asignado"
        
        if obj.usuario:
            nombre_solicitante = f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip()
            documento_identidad = obj.usuario.ci or "No asignado"
            cargo = obj.usuario.cargo or "No asignado"
        
        # Procesar detalle de gastos con el formato específico
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        
        # Obtener datos de responsables
        nombre_responsable = "No asignado"
        if obj.responsable:
            nombre_responsable = f"{obj.responsable.nombre or ''} {obj.responsable.paterno or ''}".strip()
        
        nombre_coordinador = "No asignado"
        if obj.coordinador:
            nombre_coordinador = f"{obj.coordinador.nombre or ''} {obj.coordinador.paterno or ''}".strip()
        
        # Obtener actividad
        actividad = obj.actividad
        
        # Mapeo de estados
        estados_map = dict(ActividadPei.ESTADOS_ACTIVIDAD)
        
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"SR-ACT-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            
            # Información del solicitante
            'nombre_solicitante': nombre_solicitante,
            'documento_identidad': documento_identidad,
            'cargo': cargo,
            
            # Información de la actividad
            'codigo_actividad': actividad.codigo if actividad else "No asignado",
            'nombre_actividad': actividad.nombreCorto if actividad else "No especificado",
            'estado_actividad': estados_map.get(actividad.estado, actividad.estado) if actividad and actividad.estado else "N/A",
            'fecha_ejecucion': obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada",
            'descripcion_actividad': obj.descripcion_actividad or (actividad.descripcion if actividad else "No especificada"),
            'objetivo_actividad': obj.objetivo_actividad or (actividad.objetivo_de_actividad if actividad else "No especificado"),
            
            # Información de pago
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'total_monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos_calculado,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            
            # Información de validaciones
            'nombre_responsable': nombre_responsable,
            'nombre_coordinador': nombre_coordinador,
            
            # Fuentes de financiamiento
            'fuentes_financiamiento': self._procesar_fuentes_financiamiento(actividad),
            
            # Presupuesto de actividad
            'presupuesto_actividad': float(actividad.presupuesto) if actividad and actividad.presupuesto else 0,
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE REEMBOLSO',
            'subtipo_documento': 'Actividad PEI',
        }
        
        # ===== UNIFICAR CON EL MISMO MÉTODO QUE EL ORIGINAL =====
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        # ========================================================
        
        return context
    
    def _get_nombre_completo(self, usuario):
        """Obtiene nombre completo de cualquier usuario"""
        if not usuario:
            return "No asignado"
        
        partes = []
        if usuario.nombre:
            partes.append(usuario.nombre)
        if usuario.paterno:
            partes.append(usuario.paterno)
        if usuario.materno:
            partes.append(usuario.materno)
        
        return " ".join(partes) if partes else str(usuario)
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del reembolso SIN observaciones
        """
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_gastos, total_monto
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                import json
                data_dict = json.loads(data_dict)
            
            items_list = []
            if isinstance(data_dict, dict) and 'items' in data_dict:
                items_list = data_dict['items']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            for index, item in enumerate(items_list):
                if isinstance(item, dict):
                    # Formatear fecha
                    fecha_gasto = "No especificada"
                    if item.get('fecha'):
                        try:
                            fecha_obj = datetime.strptime(item['fecha'], '%Y-%m-%d')
                            fecha_gasto = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            fecha_gasto = item['fecha']
                    
                    partida = item.get('partida') or item.get('partida_sf') or f"{index + 1}"
                    factura_recibo = item.get('factura_recibo') or item.get('factura') or item.get('recibo') or '-'
                    concepto = item.get('concepto') or item.get('descripcion') or f"Gasto {index + 1}"
                    
                    monto_raw = item.get('monto') or item.get('valor') or item.get('importe') or 0
                    try:
                        monto = float(monto_raw)
                        total_monto += monto
                    except (ValueError, TypeError):
                        monto = 0.0
                    
                    detalle_gastos.append({
                        'indice': index + 1,
                        'fecha': fecha_gasto,
                        'partida': str(partida),
                        'factura_recibo': str(factura_recibo),
                        'concepto': str(concepto),
                        'monto': monto,
                    })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos de reembolso: {e}")
        
        return detalle_gastos, total_monto
    
    def _procesar_fuentes_financiamiento(self, actividad):
        """Procesa las fuentes de financiamiento de la actividad"""
        fuentes_financiamiento = []
        if actividad and actividad.procedencia_fondos:
            try:
                if isinstance(actividad.procedencia_fondos, list):
                    for fuente in actividad.procedencia_fondos:
                        if isinstance(fuente, dict):
                            fuentes_financiamiento.append({
                                'nombre': fuente.get('nombre', fuente.get('descripcion', 'Sin nombre')),
                                'monto': float(fuente.get('monto', fuente.get('valor', 0)))
                            })
            except Exception as e:
                print(f"Error procesando fuentes de financiamiento: {e}")
        
        return fuentes_financiamiento
    
    def _procesar_datos_transferencia(self, obj):
        """
        Procesa los datos de forma de pago (IGUAL QUE EN EL ORIGINAL)
        """
        datos_forma_pago = {
            'tipo': 'otros',
            'otros': {},
            'transferencia': {},
            'mostrar_transferencia': False,
            'mostrar_otros': False,
            'mostrar_efectivo': False,
            'mostrar_cheque': False,
        }
        
        if not obj.datos_forma_pago:
            return datos_forma_pago
        
        try:
            if isinstance(obj.datos_forma_pago, dict):
                datos_forma_pago.update(obj.datos_forma_pago)
                
                # Determinar según forma de pago
                if obj.formaPago:
                    forma_lower = obj.formaPago.formaPago.lower()
                    
                    if 'transferencia' in forma_lower or 'tb' in forma_lower:
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                    elif 'cheque' in forma_lower or 'che' in forma_lower:
                        datos_forma_pago['tipo'] = 'cheque'
                        datos_forma_pago['mostrar_cheque'] = True
                    elif 'efectivo' in forma_lower or 'efec' in forma_lower:
                        datos_forma_pago['tipo'] = 'efectivo'
                        datos_forma_pago['mostrar_efectivo'] = True
                    else:
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
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        numero = obj.numeroFormulario or f"SR-ACT-{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Reembolso_Actividad_PEI_{numero_limpio}.pdf"
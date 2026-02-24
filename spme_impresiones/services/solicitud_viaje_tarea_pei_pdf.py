# services/solicitud_viaje_tarea_pei_pdf.py
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViajeActPei
import json
from datetime import datetime

class SolicitudViajeTareaPeiPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje de Tarea PEI (exclusivo para Tareas)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_tarea_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Viaje de Tarea PEI
        """
        if not isinstance(obj, SolicitudViajeActPei):
            raise ValueError("El objeto debe ser una instancia de SolicitudViajeActPei")
        
        # Validar que sea una solicitud con tarea
        if not obj.tarea:
            raise ValueError("Este generador es solo para solicitudes con tarea")
        
        try:
            # Formatear fechas
            fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
            fecha_evento = obj.fechaEvento.strftime('%d/%m/%Y') if obj.fechaEvento else "No especificada"
            
            # Obtener datos del USUARIO (solicitante)
            usuario_data = self._get_usuario_data(obj)
            
            # Obtener datos de la tarea
            tarea_data = self._get_tarea_data(obj)
            
            # Obtener datos de la actividad (padre)
            actividad_data = self._get_actividad_data(obj)
            
            # Procesar detalle de gastos
            detalle_gastos, total_calculado = self._procesar_detalle_gastos(obj)
            
            # Procesar datos de transferencia / forma de pago
            datos_forma_pago = self._procesar_datos_transferencia(obj)
            
            # Obtener forma de pago texto
            forma_pago_texto = "No especificada"
            codigo_pago = None
            if obj.formaPago:
                codigo_pago = obj.formaPago.codigo
                forma_pago_texto = obj.formaPago.formaPago
            else:
                codigo_pago = None
            
            # Construir beneficiario_info con la estructura correcta
            beneficiario_info = self._construir_beneficiario_info(obj, datos_forma_pago)
            
            # Validaciones con datos correctos de responsables
            responsable_nombre = self._get_nombre_responsable(obj)
            coordinador_nombre = self._get_nombre_coordinador(obj)
            
            context = {
                # Datos básicos del formulario
                'numero_formulario': obj.numeroFormulario or f"SV-PEI-T-{obj.id:04d}",
                'fecha_emision': fecha_solicitud,
                'tipo_documento': 'SOLICITUD DE VIAJE - TAREA PEI',
                'subtipo_documento': 'SV-PEI-T',
                
                # Datos del USUARIO (solicitante)
                'solicitante': usuario_data,
                
                # Datos de la tarea
                'tarea': tarea_data,
                
                # Datos de la actividad (padre)
                'actividad': actividad_data,
                
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
                'fecha_solicitud': fecha_solicitud,
                'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else 0.00,
                
                # Tipos de pago
                'forma_pago': forma_pago_texto,
                'tipo_pago': codigo_pago,
                'beneficiario_info': beneficiario_info,
                'datos_forma_pago': datos_forma_pago,
                
                # Detalle de gastos
                'detalle_gastos': detalle_gastos,
                'total_calculado': total_calculado,
                'tiene_detalle': len(detalle_gastos) > 0,
                'cantidad_items': len(detalle_gastos),
                
                # Validaciones
                'validacion_responsable': obj.validacionResponsable,
                'responsable_nombre': responsable_nombre,
                'validacion_coordinador': obj.validacionCoordinador,
                'coordinador_nombre': coordinador_nombre,
                
                # Bloqueo de iconos
                'bloqueo_iconos': obj.bloquearIconos,
            }
            
            return context
            
        except Exception as e:
            print(f"ERROR CRÍTICO en prepare_context: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _procesar_datos_transferencia(self, obj):
        """
        Procesa los datos de forma de pago del formulario
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
                
                # Determinar qué tipo de pago mostrar
                tiene_datos_otros = datos_forma_pago.get('otros', {}).get('nombre_otros')
                tiene_datos_transferencia = datos_forma_pago.get('transferencia', {}).get('nombre_transferencia')
                
                # Verificar por el tipo de forma de pago
                if obj.formaPago:
                    if obj.formaPago.codigo == 'TB' or 'transferencia' in obj.formaPago.formaPago.lower():
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = False
                        datos_forma_pago['mostrar_cheque'] = False
                    elif obj.formaPago.codigo == 'CHE' or 'cheque' in obj.formaPago.formaPago.lower():
                        datos_forma_pago['tipo'] = 'cheque'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = True
                        datos_forma_pago['mostrar_efectivo'] = False
                        datos_forma_pago['mostrar_cheque'] = True
                    elif obj.formaPago.codigo == 'EFEC' or 'efectivo' in obj.formaPago.formaPago.lower():
                        datos_forma_pago['tipo'] = 'efectivo'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = True
                        datos_forma_pago['mostrar_cheque'] = False
                    else:
                        datos_forma_pago['tipo'] = 'otros'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = True
                        datos_forma_pago['mostrar_efectivo'] = False
                        datos_forma_pago['mostrar_cheque'] = False
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
    
    def _construir_beneficiario_info(self, obj, datos_forma_pago):
        """
        Construye la estructura beneficiario_info a partir de datos_forma_pago
        """
        beneficiario_info = {
            'datos': {},
            'tipo_pago': None,
            'tipo_display': 'No especificada',
            'tiene_datos': False
        }
        
        if not obj.formaPago:
            return beneficiario_info
        
        codigo_pago = obj.formaPago.codigo
        beneficiario_info['tipo_pago'] = codigo_pago
        
        # Establecer texto de display
        if codigo_pago == 'EFEC':
            beneficiario_info['tipo_display'] = 'Efectivo'
        elif codigo_pago == 'TB':
            beneficiario_info['tipo_display'] = 'Transferencia Bancaria'
        elif codigo_pago == 'CHE':
            beneficiario_info['tipo_display'] = 'Cheque'
        else:
            beneficiario_info['tipo_display'] = obj.formaPago.formaPago
        
        # Extraer datos según el tipo
        if codigo_pago == 'EFEC':  # EFECTIVO - usa "otros"
            otros = datos_forma_pago.get('otros', {})
            beneficiario_info['datos'] = {
                'nombre': otros.get('nombre_otros', ''),
                'ci': otros.get('ci_otros', ''),
            }
            
        elif codigo_pago == 'TB':  # TRANSFERENCIA BANCARIA - usa "transferencia"
            transferencia = datos_forma_pago.get('transferencia', {})
            beneficiario_info['datos'] = {
                'nombre': transferencia.get('nombre_transferencia', ''),
                'ci': transferencia.get('ci_transferencia', ''),
                'banco': transferencia.get('entidad_bancaria', ''),
                'tipo_cuenta': transferencia.get('tipo_cuenta', ''),
                'numero_cuenta': transferencia.get('numero_cuenta', ''),
            }
            
        elif codigo_pago == 'CHE':  # CHEQUE - usa "otros"
            otros = datos_forma_pago.get('otros', {})
            beneficiario_info['datos'] = {
                'nombre': otros.get('nombre_otros', ''),
                'ci': otros.get('ci_otros', ''),
            }
        else:
            # Para otros tipos de pago, intentar usar datos de otros
            otros = datos_forma_pago.get('otros', {})
            if otros:
                beneficiario_info['datos'] = {
                    'nombre': otros.get('nombre_otros', ''),
                    'ci': otros.get('ci_otros', ''),
                }
        
        # Verificar si hay datos
        beneficiario_info['tiene_datos'] = any(beneficiario_info['datos'].values())
        
        return beneficiario_info
    
    def _get_usuario_data(self, obj):
        """Obtiene datos del usuario"""
        if not obj.usuario:
            return {
                'nombre_completo': "No especificado",
                'documento_identidad': "No especificado",
                'cargo': "No especificado",
                'correo': "No especificado",
                'username': "No especificado",
                'banco': "No especificado",
                'numero_cuenta': "No especificado",
                'tipo_cuenta': "No especificado",
            }
        
        nombre_parts = []
        if obj.usuario.nombre:
            nombre_parts.append(obj.usuario.nombre)
        if obj.usuario.paterno:
            nombre_parts.append(obj.usuario.paterno)
        if obj.usuario.materno:
            nombre_parts.append(obj.usuario.materno)
        
        return {
            'nombre_completo': " ".join(nombre_parts) or "No especificado",
            'documento_identidad': obj.usuario.ci or "No especificado",
            'cargo': obj.usuario.cargo or "No especificado",
            'correo': obj.usuario.correo or "No especificado",
            'username': obj.usuario.username or "No especificado",
            'banco': obj.usuario.banco or "No especificado",
            'numero_cuenta': obj.usuario.numero_cuenta or "No especificado",
            'tipo_cuenta': obj.usuario.tipo_cuenta or "No especificado",
        }
    
    def _get_tarea_data(self, obj):
        """Obtiene datos de la tarea"""
        if not obj.tarea:
            return {}
        
        # Mapeo de estados de tarea si existe
        estado_tarea = "No especificado"
        if hasattr(obj.tarea, 'get_estado_display'):
            estado_tarea = obj.tarea.get_estado_display()
        elif hasattr(obj.tarea, 'estado'):
            estado_tarea = obj.tarea.estado
        
        return {
            'codigo': obj.tarea.codigo or "No asignado",
            'titulo': obj.tarea.titulo or "Sin título",
            'descripcion': obj.tarea.descripcion or "Sin descripción",
            'fecha_ejecucion': obj.tarea.fecha_ejecucion.strftime('%d/%m/%Y') if hasattr(obj.tarea, 'fecha_ejecucion') and obj.tarea.fecha_ejecucion else "No especificada",
            'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if hasattr(obj.tarea, 'fecha_limite') and obj.tarea.fecha_limite else "No especificada",
            'estado': estado_tarea,
            'presupuesto': float(obj.tarea.presupuesto) if hasattr(obj.tarea, 'presupuesto') and obj.tarea.presupuesto else 0.0,
        }
    
    def _get_actividad_data(self, obj):
        """Obtiene datos de la actividad padre"""
        if not obj.actividad:
            return {}
        
        estados_map = {
            'CRD': 'Creada',
            'PLAN': 'Planificada',
            'RETR': 'Retraso',
            'REPROG': 'Reprogramación',
            'EJEC': 'En Ejecución',
            'REP': 'En Reporte',
            'FIN': 'Finalizado',
        }
        
        return {
            'codigo': obj.actividad.codigo or "No asignado",
            'nombre': obj.actividad.nombreCorto or "Sin nombre",
            'estado': estados_map.get(obj.actividad.estado, obj.actividad.estado) if obj.actividad.estado else "No especificado",
            'responsable': self._get_nombre_completo(obj.actividad.responsable) if obj.actividad.responsable else "No asignado",
        }
    
    def _get_nombre_completo(self, usuario):
        """Obtiene nombre completo de un usuario"""
        if not usuario:
            return "No asignado"
        
        parts = []
        if usuario.nombre:
            parts.append(usuario.nombre)
        if usuario.paterno:
            parts.append(usuario.paterno)
        if usuario.materno:
            parts.append(usuario.materno)
        
        return " ".join(parts) if parts else "No asignado"
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del viaje
        """
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
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items = data_dict['items']
                elif 'gastos' in data_dict:
                    items = data_dict['gastos']
                elif 'detalle' in data_dict:
                    items = data_dict['detalle']
                else:
                    # Si es un diccionario con una sola entrada
                    items = [data_dict]
            elif isinstance(data_dict, list):
                items = data_dict
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Formatear fecha
                fecha_item = item.get('fecha', '')
                if fecha_item:
                    try:
                        fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                        fecha_item = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        try:
                            fecha_obj = datetime.strptime(fecha_item, '%d/%m/%Y')
                            fecha_item = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            pass
                
                monto = float(item.get('monto', item.get('valor', 0)))
                total_calculado += monto
                
                detalle_gastos.append({
                    'fecha': fecha_item,
                    'partida': item.get('partida', item.get('codigo', '')),
                    'descripcion': item.get('descripcion', '') or item.get('concepto', '') or item.get('detalle', ''),
                    'factura_recibo': item.get('factura_recibo', item.get('factura', item.get('recibo', ''))),
                    'monto': monto,
                })
                
        except Exception as e:
            print(f"Error procesando detalle de gastos: {e}")
        
        return detalle_gastos, total_calculado
    
    def _get_nombre_responsable(self, obj):
        """Obtiene nombre completo del responsable"""
        if not obj.responsable:
            return "No asignado"
        
        parts = []
        if obj.responsable.nombre:
            parts.append(obj.responsable.nombre)
        if obj.responsable.paterno:
            parts.append(obj.responsable.paterno)
        if obj.responsable.materno:
            parts.append(obj.responsable.materno)
        
        return " ".join(parts) if parts else "No asignado"
    
    def _get_nombre_coordinador(self, obj):
        """Obtiene nombre completo del coordinador"""
        if not obj.coordinador:
            return "No asignado"
        
        parts = []
        if obj.coordinador.nombre:
            parts.append(obj.coordinador.nombre)
        if obj.coordinador.paterno:
            parts.append(obj.coordinador.paterno)
        if obj.coordinador.materno:
            parts.append(obj.coordinador.materno)
        
        return " ".join(parts) if parts else "No asignado"
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF para solicitudes de viaje de tareas PEI
        """
        numero = obj.numeroFormulario or f"SV-PEI-T-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        
        # Limpiar caracteres especiales
        import re
        nombre_solicitante = re.sub(r'[^a-zA-Z0-9]', '', nombre_solicitante)
        numero_limpio = re.sub(r'[^a-zA-Z0-9_-]', '', numero)
        
        return f"Solicitud_Viaje_Tarea_PEI_{nombre_solicitante}_{numero_limpio}.pdf"
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudPagoDirecto

class SolicitudPagoDirectoTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Pago Directo (exclusivo para Tareas)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_pago_directo_tarea_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Pago Directo de Tarea
        """
        if not isinstance(obj, SolicitudPagoDirecto):
            raise ValueError("El objeto debe ser una instancia de SolicitudPagoDirecto")
        
        try:
            # Formatear fechas
            fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
            fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada"
            
            # Obtener datos del USUARIO (solicitante)
            usuario_data = self._get_usuario_data(obj)
            
            # Obtener datos de la tarea si existe
            tarea_data = self._get_tarea_data(obj)
            
            # Procesar detalle de destino de fondos
            detalle_fondos, total_calculado = self._procesar_detalle_fondos(obj)
            
            # ===== PROCESAR DATOS DE FORMA DE PAGO =====
            datos_forma_pago = self._procesar_datos_transferencia(obj)
            
            # Obtener forma de pago texto
            forma_pago_texto = "No especificada"
            codigo_pago = None
            
            if obj.formaPago:
                codigo_pago = obj.formaPago.codigo
                if codigo_pago == 'EFEC':
                    forma_pago_texto = 'Efectivo'
                elif codigo_pago == 'TB':
                    forma_pago_texto = 'Transferencia Bancaria'
                elif codigo_pago == 'CHE':
                    forma_pago_texto = 'Cheque'
                else:
                    # Fallback a la descripción si no coincide
                    forma_pago_texto = obj.formaPago.formaPago or "No especificada"
            
            # Construir beneficiario_info
            beneficiario_info = self._construir_beneficiario_info(obj, datos_forma_pago)
            # ===========================================
            
            # Obtener nombres de responsables
            contador_nombre = self._get_nombre_contador(obj)
            coordinador_nombre = self._get_nombre_coordinador(obj)
            
            # Obtener datos de actividad (si existe a través de la tarea)
            actividad_data = self._get_actividad_data(obj)
            
            context = {
                # Datos básicos del formulario
                'numero_formulario': obj.numeroFormulario or f"SPD-{obj.id:04d}",
                'fecha_emision': fecha_solicitud,
                'tipo_documento': 'SOLICITUD DE PAGO DIRECTO - TAREA',
                'subtipo_documento': 'SPD-T',
                
                # Datos del USUARIO (solicitante)
                'solicitante': usuario_data,
                
                # Datos de la tarea
                'tarea': tarea_data,
                
                # Datos de actividad
                'actividad': actividad_data,
                
                # Datos específicos del pago directo
                'lugar_solicitud': obj.lugarSolicitud or "No especificado",
                'fecha_solicitud': fecha_solicitud,
                'fecha_realizacion': fecha_realizacion,
                'descripcion_actividad': obj.descripcion_actividad or "No especificada",
                'objetivo_actividad': obj.objetivo_actividad or "No especificado",
                'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else 0.00,
                
                # ===== TIPOS DE PAGO =====
                'forma_pago': forma_pago_texto,
                'tipo_pago': codigo_pago,
                'beneficiario_info': beneficiario_info,
                'datos_forma_pago': datos_forma_pago,
                # =========================
                
                # Detalle de fondos
                'detalle_fondos': detalle_fondos,
                'total_calculado': total_calculado,
                'tiene_detalle': len(detalle_fondos) > 0,
                'cantidad_items': len(detalle_fondos),
                
                # Validaciones
                'validacion_responsable': obj.validacionResponsable,
                'contador_nombre': contador_nombre,
                'validacion_coordinador': obj.validacionCoordinador,
                'coordinador_nombre': coordinador_nombre,
                
                # Bloqueo de iconos
                'bloqueo_iconos': obj.bloquearIconosSolFondos,
            }
            
            return context
            
        except Exception as e:
            print(f"ERROR CRÍTICO en prepare_context (Pago Directo): {e}")
            import traceback
            traceback.print_exc()
            raise
    
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
                'permisos': "No especificado",
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
            'permisos': obj.usuario.permisos or "No especificado",
        }
    
    def _get_tarea_data(self, obj):
        """Obtiene datos de la tarea"""
        if not obj.tarea:
            return {}
        
        return {
            'codigo': obj.tarea.codigo or "No asignado",
            'titulo': obj.tarea.titulo or "Sin título",
            'descripcion': obj.tarea.descripcion or "Sin descripción",
            'fecha_ejecucion': obj.tarea.fecha_ejecucion.strftime('%d/%m/%Y') if obj.tarea.fecha_ejecucion else "No especificada",
            'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if obj.tarea.fecha_limite else "No especificada",
            'estado': obj.tarea.get_estado_display() if hasattr(obj.tarea, 'get_estado_display') else "No especificado",
            'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0.0,
        }
    
    def _get_actividad_data(self, obj):
        """Obtiene datos de la actividad a través de la tarea"""
        if not obj.tarea or not obj.tarea.actividad:
            return {}
        
        actividad = obj.tarea.actividad
        return {
            'codigo': actividad.codigo or "No asignado",
            'nombre_corto': actividad.nombreCorto or "Sin nombre",
            'descripcion': actividad.descripcion or "Sin descripción",
            'objetivo': actividad.objetivo_de_actividad or "Sin objetivo",
        }
    
    def _procesar_detalle_fondos(self, obj):
        """
        Procesa el detalle de destino de fondos
        Estructura esperada: {"items": [{"partida_sf": "...", "concepto": "...", "monto": ...}]}
        """
        detalle_fondos = []
        total_calculado = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_fondos, total_calculado
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            # Si es string, parsear JSON
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    print(f"Error parseando JSON de detalleDestinoFondos")
                    return detalle_fondos, total_calculado
            
            # Extraer items
            items = []
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items = data_dict['items']
                elif 'detalle' in data_dict:
                    items = data_dict['detalle']
            elif isinstance(data_dict, list):
                items = data_dict
            
            for index, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    continue
                
                try:
                    monto = float(item.get('monto', 0))
                    total_calculado += monto
                    
                    # Formatear fecha si existe
                    fecha_item = item.get('fecha', '')
                    if fecha_item:
                        try:
                            from datetime import datetime
                            fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                            fecha_item = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            pass
                    
                    partida = (
                        item.get('partida_sf') or 
                        item.get('partida') or 
                        item.get('codigo') or 
                        ''
                    )

                    fuente = (
                        item.get('fuente') or 
                        item.get('fuente_financiamiento') or 
                        item.get('fuente_fin') or 
                        item.get('origen') or 
                        'No especificada'
                    )
                    
                    detalle_fondos.append({
                        'numero': index,
                        'partida_sf': item.get('partida_sf', ''),
                        'fuente': str(fuente),    
                        'concepto': item.get('concepto', '') or item.get('descripcion', ''),
                        'monto': monto,
                        'factura_recibo': item.get('factura_recibo', ''),
                        'fecha': fecha_item,
                        'observaciones': item.get('observaciones', ''),
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error procesando item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error procesando detalle de fondos: {e}")
            import traceback
            traceback.print_exc()
        
        return detalle_fondos, total_calculado
    
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
                
                # Verificar por el tipo de forma de pago usando el código
                if obj.formaPago:
                    codigo = obj.formaPago.codigo
                    if codigo == 'TB':
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = False
                        datos_forma_pago['mostrar_cheque'] = False
                    elif codigo == 'CHE':
                        datos_forma_pago['tipo'] = 'cheque'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = False
                        datos_forma_pago['mostrar_cheque'] = True
                    elif codigo == 'EFEC':
                        datos_forma_pago['tipo'] = 'efectivo'
                        datos_forma_pago['mostrar_transferencia'] = False
                        datos_forma_pago['mostrar_otros'] = False
                        datos_forma_pago['mostrar_efectivo'] = True
                        datos_forma_pago['mostrar_cheque'] = False
                    else:
                        datos_forma_pago['tipo'] = 'otros'
                        datos_forma_pago['mostrar_otros'] = True
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
            beneficiario_info['tipo_display'] = obj.formaPago.formaPago or "No especificada"
        
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
        else:  # OTROS - intentar con "otros"
            otros = datos_forma_pago.get('otros', {})
            beneficiario_info['datos'] = {
                'nombre': otros.get('nombre_otros', ''),
                'ci': otros.get('ci_otros', ''),
            }
        
        # Verificar si hay datos
        beneficiario_info['tiene_datos'] = any(beneficiario_info['datos'].values())
        
        return beneficiario_info
    
    def _get_nombre_contador(self, obj):
        """Obtiene nombre completo del contador"""
        if not obj.contador:
            return "No asignado"
        
        parts = []
        if obj.contador.nombre:
            parts.append(obj.contador.nombre)
        if obj.contador.paterno:
            parts.append(obj.contador.paterno)
        if obj.contador.materno:
            parts.append(obj.contador.materno)
        
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
        Genera el nombre del archivo PDF para pagos directos de tareas
        """
        numero = obj.numeroFormulario or f"SPD-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        
        return f"Pago_Directo_Tarea_{nombre_solicitante}_{numero}.pdf"
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudPagoDirecto 

class SolicitudPagoDirectoPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Pago Directo
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_pago_directo_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Pago Directo
        """
        if not isinstance(obj, SolicitudPagoDirecto):
            raise ValueError("El objeto debe ser una instancia de SolicitudPagoDirecto")
        
        # Obtener datos del solicitante
        nombre_solicitante = "No asignado"
        documento_identidad = "No asignado"
        cargo = "No asignado"
        
        if obj.usuario:
            nombre_solicitante = f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip()
            documento_identidad = obj.usuario.ci or "No asignado"
            cargo = obj.usuario.cargo or "No asignado"
        
        # Procesar detalle de gastos
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        
        # Obtener datos de validaciones
        nombre_contador = "No asignado"
        if obj.contador:
            nombre_contador = f"{obj.contador.nombre or ''} {obj.contador.paterno or ''}".strip()
        
        nombre_coordinador = "No asignado"
        if obj.coordinador:
            nombre_coordinador = f"{obj.coordinador.nombre or ''} {obj.coordinador.paterno or ''}".strip()
        
        # Construir contexto
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"SPD-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            
            # Información del solicitante
            'nombre_solicitante': nombre_solicitante,
            'documento_identidad': documento_identidad,
            'cargo': cargo,
            
            # Información de la actividad
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'estado_actividad': self._get_estado_actividad(obj),
            'fecha_ejecucion': obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada",
            'descripcion_actividad': obj.descripcion_actividad or "No especificada",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            
            # Información de pago
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos_calculado,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            
            # Información de validaciones
            'nombre_contador': nombre_contador,
            'nombre_coordinador': nombre_coordinador,
            
            # Fuentes de financiamiento
            'fuentes_financiamiento': self._procesar_fuentes_financiamiento(obj),
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE PAGO DIRECTO',
            'subtipo_documento': 'F-04',
        }
        
        # ===== UNIFICAR CON EL MISMO MÉTODO QUE FONDOS =====
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        # ==================================================
        
        return context
    
    def _procesar_datos_transferencia(self, obj):
        """
        Procesa los datos de forma de pago (IGUAL QUE EN FONDOS)
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
    
    def _get_estado_actividad(self, obj):
        """Obtiene el estado de la actividad formateado"""
        if obj.actividad and obj.actividad.estado:
            estado = obj.actividad.estado
            estados_map = {
                'CRD': 'Creada',
                'PLAN': 'Planificada',
                'RETR': 'Retraso',
                'REPROG': 'Reprogramación',
                'EJEC': 'En Ejecución',
                'REP': 'En Reporte',
                'FIN': 'Finalizado',
            }
            return estados_map.get(estado, estado)
        return "No especificado"
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos para pago directo
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
                    partida = item.get('partida_sf') or item.get('partida') or f"{index + 1}"
                    
                    fuente = (
                        item.get('fuente') or 
                        item.get('fuente_financiamiento') or 
                        item.get('fuente_fin') or 
                        item.get('origen') or 
                        'No especificada'
                    )
                
                    concepto = item.get('concepto') or item.get('descripcion') or f"Item {index + 1}"
                    
                    monto_raw = item.get('monto') or item.get('valor') or 0
                    try:
                        monto = float(monto_raw)
                        total_monto += monto
                    except (ValueError, TypeError):
                        monto = 0.0
                    
                    detalle_gastos.append({
                        'indice': index + 1,
                        'partida': str(partida),
                        'fuente': fuente,
                        'descripcion_gasto': str(concepto),
                        'monto': monto,
                    })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos: {e}")
        
        return detalle_gastos, total_monto
    
    def _procesar_fuentes_financiamiento(self, obj):
        """Procesa las fuentes de financiamiento de la actividad"""
        fuentes_financiamiento = []
        if obj.actividad and obj.actividad.procedencia_fondos:
            try:
                if isinstance(obj.actividad.procedencia_fondos, list):
                    for fuente in obj.actividad.procedencia_fondos:
                        if isinstance(fuente, dict):
                            fuentes_financiamiento.append({
                                'nombre': fuente.get('nombre', fuente.get('descripcion', 'Sin nombre')),
                                'monto': float(fuente.get('monto', fuente.get('valor', 0)))
                            })
            except Exception as e:
                print(f"Error procesando fuentes de financiamiento: {e}")
        
        return fuentes_financiamiento
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        numero = obj.numeroFormulario or f"SPD{obj.id:04d}"
        return f"Solicitud_Pago_Directo_{numero}.pdf"
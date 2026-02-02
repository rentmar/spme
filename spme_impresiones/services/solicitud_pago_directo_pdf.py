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
        
        # Procesar datos de forma de pago
        datos_forma_pago = self._procesar_datos_forma_pago(obj)
        
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
            
            # Datos de forma de pago
            'datos_forma_pago': datos_forma_pago,
            
            # Fuentes de financiamiento
            'fuentes_financiamiento': self._procesar_fuentes_financiamiento(obj),
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE PAGO DIRECTO',
            'subtipo_documento': 'F-04',
        }
        
        return context
    
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
        Formato esperado: {"items": [{"partida_sf": "...", "concepto": "...", "monto": ...}]}
        """
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_gastos, total_monto
        
        try:
            # Normalizar datos
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                import json
                data_dict = json.loads(data_dict)
            
            # Extraer items
            items_list = []
            if isinstance(data_dict, dict) and 'items' in data_dict:
                items_list = data_dict['items']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            # Procesar cada item
            for index, item in enumerate(items_list):
                if isinstance(item, dict):
                    partida = item.get('partida_sf') or item.get('partida') or item.get('codigo') or f"{index + 1}"
                    concepto = item.get('concepto') or item.get('descripcion') or item.get('descripcionGasto') or f"Item {index + 1}"
                    
                    monto_raw = item.get('monto') or item.get('valor') or item.get('importe') or 0
                    try:
                        monto = float(monto_raw)
                        total_monto += monto
                    except (ValueError, TypeError):
                        monto = 0.0
                    
                    observaciones = item.get('observaciones') or item.get('observacion') or '-'
                    
                    detalle_gastos.append({
                        'indice': index + 1,
                        'partida': str(partida),
                        'descripcion_gasto': str(concepto),
                        'monto': monto,
                        'observaciones': str(observaciones),
                    })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos para pago directo: {e}")
        
        return detalle_gastos, total_monto
    
    def _procesar_datos_forma_pago(self, obj):
        """
        Procesa los datos de forma de pago
        Formato: {"otros": {...}, "transferencia": {...}}
        """
        datos_pago = {
            'tipo': 'efectivo',
            'mostrar_transferencia': False,
            'mostrar_otros': False,
            'transferencia': {
                'nombre_transferencia': '',
                'ci_transferencia': '',
                'entidad_bancaria': '',
                'tipo_cuenta': '',
                'numero_cuenta': '',
            },
            'otros': {
                'nombre_otros': '',
                'ci_otros': '',
            }
        }
        
        # Determinar tipo basado en forma de pago
        if obj.formaPago:
            forma = obj.formaPago.formaPago.lower()
            if 'transferencia' in forma:
                datos_pago['tipo'] = 'transferencia'
                datos_pago['mostrar_transferencia'] = True
            elif 'otros' in forma or 'tercero' in forma:
                datos_pago['tipo'] = 'otros'
                datos_pago['mostrar_otros'] = True
        
        # Procesar datos_forma_pago si existe
        if obj.datos_forma_pago:
            try:
                if isinstance(obj.datos_forma_pago, str):
                    import json
                    datos_forma_pago = json.loads(obj.datos_forma_pago)
                else:
                    datos_forma_pago = obj.datos_forma_pago
                
                if isinstance(datos_forma_pago, dict):
                    # Datos de transferencia
                    if 'transferencia' in datos_forma_pago:
                        datos_pago['transferencia'].update(datos_forma_pago['transferencia'])
                        if datos_forma_pago['transferencia'].get('nombre_transferencia'):
                            datos_pago['mostrar_transferencia'] = True
                            datos_pago['mostrar_otros'] = False
                    
                    # Datos de otros
                    if 'otros' in datos_forma_pago:
                        datos_pago['otros'].update(datos_forma_pago['otros'])
                        if datos_forma_pago['otros'].get('nombre_otros'):
                            datos_pago['mostrar_otros'] = True
                            datos_pago['mostrar_transferencia'] = False
                            
            except Exception as e:
                print(f"Error procesando datos_forma_pago: {e}")
        
        # Completar datos faltantes con información del usuario
        if obj.usuario:
            nombre_completo = f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip()
            ci = obj.usuario.ci or ''
            
            if datos_pago['mostrar_transferencia'] and not datos_pago['transferencia'].get('nombre_transferencia'):
                datos_pago['transferencia']['nombre_transferencia'] = nombre_completo
                datos_pago['transferencia']['ci_transferencia'] = ci
                datos_pago['transferencia']['entidad_bancaria'] = obj.usuario.banco or ''
                datos_pago['transferencia']['numero_cuenta'] = obj.usuario.numero_cuenta or ''
                datos_pago['transferencia']['tipo_cuenta'] = obj.usuario.tipo_cuenta or ''
            
            elif datos_pago['mostrar_otros'] and not datos_pago['otros'].get('nombre_otros'):
                datos_pago['otros']['nombre_otros'] = nombre_completo
                datos_pago['otros']['ci_otros'] = ci
        
        return datos_pago
    
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
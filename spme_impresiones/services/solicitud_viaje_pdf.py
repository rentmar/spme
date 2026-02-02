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
        
        # Procesar detalle de gastos si existe
        detalle_gastos = []
        total_gastos = 0.0
        
        if obj.detalleGasto:
            detalle_gastos, total_gastos = self._procesar_detalle_gastos(obj)
        
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
            'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'total_gastos': total_gastos,
            
            # Información de validaciones
            'nombre_responsable': nombre_responsable,
            'nombre_coordinador': nombre_coordinador,
            
            # Información de actividad si existe
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            
            # Datos de forma de pago
            'datos_forma_pago': self._procesar_datos_forma_pago(obj),
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE VIAJE',
            'subtipo_documento': 'F-03',
        }
        
        return context
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del viaje
        Formato esperado: Lista de items con conceptos de gastos de viaje
        """
        detalle_gastos = []
        total_gastos = 0.0
        
        if not obj.detalleGasto:
            return detalle_gastos, total_gastos
        
        try:
            # El formato puede variar, manejamos diferentes posibilidades
            items = []
            
            if isinstance(obj.detalleGasto, dict):
                if 'items' in obj.detalleGasto:
                    items = obj.detalleGasto['items']
                elif 'gastos' in obj.detalleGasto:
                    items = obj.detalleGasto['gastos']
                elif 'detalle' in obj.detalleGasto:
                    items = obj.detalleGasto['detalle']
            
            elif isinstance(obj.detalleGasto, list):
                items = obj.detalleGasto
            
            # Procesar cada item
            for index, item in enumerate(items):
                if isinstance(item, dict):
                    # Campos comunes para gastos de viaje
                    concepto = item.get('concepto') or item.get('descripcion') or item.get('item') or f"Gasto {index + 1}"
                    cantidad = float(item.get('cantidad', 1))
                    unidad = item.get('unidad', '')
                    precio_unitario = float(item.get('precio_unitario', item.get('precio', 0)))
                    subtotal = float(item.get('subtotal', cantidad * precio_unitario))
                    
                    total_gastos += subtotal
                    
                    detalle_gastos.append({
                        'indice': index + 1,
                        'concepto': concepto,
                        'cantidad': cantidad,
                        'unidad': unidad,
                        'precio_unitario': precio_unitario,
                        'subtotal': subtotal,
                        'observaciones': item.get('observaciones', ''),
                    })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos de viaje: {e}")
        
        return detalle_gastos, total_gastos
    
    def _procesar_datos_forma_pago(self, obj):
        """
        Procesa los datos de forma de pago específicos para viaje
        Formato esperado:
        {
            "otros": {"nombre_otros": "...", "ci_otros": "..."},
            "transferencia": {"nombre_transferencia": "...", "ci_transferencia": "...", ...}
        }
        """
        datos_pago = {
            'tipo': 'efectivo',  # default
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
            },
            'mostrar_transferencia': False,
            'mostrar_otros': False,
        }
        
        # Determinar tipo basado en forma de pago seleccionada
        if obj.formaPago:
            forma_pago_lower = obj.formaPago.formaPago.lower()
            
            if 'transferencia' in forma_pago_lower:
                datos_pago['tipo'] = 'transferencia'
                datos_pago['mostrar_transferencia'] = True
            elif 'otros' in forma_pago_lower or 'tercero' in forma_pago_lower:
                datos_pago['tipo'] = 'otros'
                datos_pago['mostrar_otros'] = True
            else:
                datos_pago['tipo'] = 'efectivo'
        
        # Procesar datos_forma_pago si existe
        if obj.datos_forma_pago:
            try:
                # Si es string, parsear como JSON
                if isinstance(obj.datos_forma_pago, str):
                    import json
                    datos_forma_pago = json.loads(obj.datos_forma_pago)
                else:
                    datos_forma_pago = obj.datos_forma_pago
                
                # Actualizar datos de transferencia si existen
                if 'transferencia' in datos_forma_pago and isinstance(datos_forma_pago['transferencia'], dict):
                    datos_pago['transferencia'].update(datos_forma_pago['transferencia'])
                
                # Actualizar datos de otros si existen
                if 'otros' in datos_forma_pago and isinstance(datos_forma_pago['otros'], dict):
                    datos_pago['otros'].update(datos_forma_pago['otros'])
                
                # Si hay datos en "otros" pero no se ha determinado tipo, mostrar otros
                if datos_pago['otros'].get('nombre_otros'):
                    datos_pago['tipo'] = 'otros'
                    datos_pago['mostrar_otros'] = True
                    datos_pago['mostrar_transferencia'] = False
                
                # Si hay datos en "transferencia" pero no se ha determinado tipo, mostrar transferencia
                if datos_pago['transferencia'].get('nombre_transferencia'):
                    datos_pago['tipo'] = 'transferencia'
                    datos_pago['mostrar_transferencia'] = True
                    datos_pago['mostrar_otros'] = False
                    
            except Exception as e:
                print(f"Error procesando datos_forma_pago: {e}")
                import traceback
                print(traceback.format_exc())
        
        # Si es transferencia y no hay datos específicos, usar datos del usuario
        if datos_pago['tipo'] == 'transferencia' and not datos_pago['transferencia'].get('nombre_transferencia'):
            if obj.usuario:
                datos_pago['transferencia'].update({
                    'nombre_transferencia': f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip(),
                    'ci_transferencia': obj.usuario.ci or '',
                    'entidad_bancaria': obj.usuario.banco or '',
                    'numero_cuenta': obj.usuario.numero_cuenta or '',
                    'tipo_cuenta': obj.usuario.tipo_cuenta or '',
                })
        
        # Si es "otros" y no hay datos específicos, usar datos del solicitante
        if datos_pago['tipo'] == 'otros' and not datos_pago['otros'].get('nombre_otros'):
            if obj.usuario:
                datos_pago['otros'].update({
                    'nombre_otros': f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip(),
                    'ci_otros': obj.usuario.ci or '',
                })
        
        # Debug: imprimir datos procesados
        print(f"[DEBUG] Tipo de pago: {datos_pago['tipo']}")
        print(f"[DEBUG] Mostrar transferencia: {datos_pago['mostrar_transferencia']}")
        print(f"[DEBUG] Mostrar otros: {datos_pago['mostrar_otros']}")
        print(f"[DEBUG] Datos transferencia: {datos_pago['transferencia']}")
        print(f"[DEBUG] Datos otros: {datos_pago['otros']}")
        
        return datos_pago
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        numero = obj.numeroFormulario or f"SV{obj.id:04d}"
        return f"Solicitud_Viaje_{numero}.pdf"
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
        
        # Formatear fechas
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
        fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada"
        
        # Obtener datos del USUARIO (solicitante)
        usuario_data = {}
        if obj.usuario:
            # Construir nombre completo
            nombre_completo_parts = []
            if obj.usuario.nombre:
                nombre_completo_parts.append(obj.usuario.nombre)
            if obj.usuario.paterno:
                nombre_completo_parts.append(obj.usuario.paterno)
            if obj.usuario.materno:
                nombre_completo_parts.append(obj.usuario.materno)
            
            nombre_completo = " ".join(nombre_completo_parts) if nombre_completo_parts else "No especificado"
            
            usuario_data = {
                'nombre_completo': nombre_completo,
                'documento_identidad': obj.usuario.ci or "No especificado",
                'cargo': obj.usuario.cargo or "No especificado",
                'correo': obj.usuario.correo or "No especificado",
                'username': obj.usuario.username or "No especificado",
                'banco': obj.usuario.banco or "No especificado",
                'numero_cuenta': obj.usuario.numero_cuenta or "No especificado",
                'tipo_cuenta': obj.usuario.tipo_cuenta or "No especificado",
                'permisos': obj.usuario.permisos or "No especificado",
            }
        else:
            usuario_data = {
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
        
        # Obtener datos de la tarea si existe
        tarea_data = {}
        if obj.tarea:
            tarea_data = {
                'codigo': obj.tarea.codigo or "No asignado",
                'titulo': obj.tarea.titulo or "Sin título",
                'descripcion': obj.tarea.descripcion or "Sin descripción",
                'fecha_ejecucion': obj.tarea.fecha_ejecucion.strftime('%d/%m/%Y') if obj.tarea.fecha_ejecucion else "No especificada",
                'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if obj.tarea.fecha_limite else "No especificada",
                'estado': obj.tarea.get_estado_display() if hasattr(obj.tarea, 'get_estado_display') else "No especificado",
                'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0.0,
            }
        
        # Procesar detalle de destino de fondos - ¡ESTRUCTURA ESPECÍFICA!
        detalle_fondos = []
        total_calculado = 0.0
        
        if obj.detalleDestinoFondos and isinstance(obj.detalleDestinoFondos, dict):
            # La estructura es: {"items": [{"partida_sf": "...", "concepto": "...", "monto": ...}, ...]}
            items = obj.detalleDestinoFondos.get('items', [])
            
            for index, item in enumerate(items, 1):
                try:
                    monto = float(item.get('monto', 0))
                    total_calculado += monto
                    
                    # Para pago directo, usamos partida_sf en lugar de partida
                    detalle_fondos.append({
                        'numero': index,
                        'partida_sf': item.get('partida_sf', ''),
                        'concepto': item.get('concepto', ''),
                        'monto': monto,
                        # Campos adicionales si existen
                        'factura_recibo': item.get('factura_recibo', ''),
                        'fecha': item.get('fecha', ''),
                        'observaciones': item.get('observaciones', ''),
                        'descripcion': item.get('descripcion', ''),
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error procesando item de pago directo: {e}")
                    continue
        
        # Forma de pago
        forma_pago = "No especificada"
        if obj.formaPago and hasattr(obj.formaPago, 'formaPago'):
            forma_pago = obj.formaPago.formaPago
        
        # Datos de transferencia
        datos_transferencia = {}
        if obj.datos_forma_pago and isinstance(obj.datos_forma_pago, dict):
            datos_transferencia = obj.datos_forma_pago
        
        # Validaciones con datos correctos
        contador_nombre = "No asignado"
        if obj.contador:
            contador_parts = []
            if obj.contador.nombre:
                contador_parts.append(obj.contador.nombre)
            if obj.contador.paterno:
                contador_parts.append(obj.contador.paterno)
            if obj.contador.materno:
                contador_parts.append(obj.contador.materno)
            contador_nombre = " ".join(contador_parts) if contador_parts else "No asignado"
        
        coordinador_nombre = "No asignado"
        if obj.coordinador:
            coordinador_parts = []
            if obj.coordinador.nombre:
                coordinador_parts.append(obj.coordinador.nombre)
            if obj.coordinador.paterno:
                coordinador_parts.append(obj.coordinador.paterno)
            if obj.coordinador.materno:
                coordinador_parts.append(obj.coordinador.materno)
            coordinador_nombre = " ".join(coordinador_parts) if coordinador_parts else "No asignado"
        
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
            
            # Datos específicos del pago directo
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'fecha_solicitud': fecha_solicitud,
            'fecha_realizacion': fecha_realizacion,
            'descripcion_actividad': obj.descripcion_actividad or "No especificada",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else 0.00,
            'forma_pago': forma_pago,
            'datos_transferencia': datos_transferencia,
            
            # Detalle de fondos - CON ESTRUCTURA CORRECTA
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
            
            # Información de depuración
            'estructura_original': str(obj.detalleDestinoFondos)[:100] if obj.detalleDestinoFondos else "Vacío",
        }
        
        return context
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF para pagos directos de tareas
        """
        numero = obj.numeroFormulario or f"SPD-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            # Tomar el primer nombre
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        
        return f"Pago_Directo_Tarea_{nombre_solicitante}_{numero}.pdf"
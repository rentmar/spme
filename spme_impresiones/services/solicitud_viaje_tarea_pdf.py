from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViaje

class SolicitudViajeTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje (exclusivo para Tareas)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_tarea_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Viaje de Tarea
        """
        if not isinstance(obj, SolicitudViaje):
            raise ValueError("El objeto debe ser una instancia de SolicitudViaje")
        
        # Formatear fechas
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
        fecha_evento = obj.fechaEvento.strftime('%d/%m/%Y') if obj.fechaEvento else "No especificada"
        
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
        
        # Procesar detalle de gastos
        detalle_gastos = []
        total_calculado = 0.0
        
        if obj.detalleGasto and isinstance(obj.detalleGasto, dict):
            # La estructura esperada: {"items": [{...}, {...}]}
            items = obj.detalleGasto.get('items', [])
            
            for item in items:
                try:
                    # Formatear fecha del item si existe
                    fecha_item = item.get('fecha', '')
                    if fecha_item:
                        try:
                            from datetime import datetime
                            fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                            fecha_item = fecha_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            fecha_item = fecha_item  # Mantener como está
                    
                    monto = float(item.get('monto', 0))
                    total_calculado += monto
                    
                    detalle_gastos.append({
                        'fecha': fecha_item,
                        'partida': item.get('partida', ''),
                        'descripcion': item.get('descripcion', '') or item.get('concepto', ''),
                        'factura_recibo': item.get('factura_recibo', ''),
                        'monto': monto,
                        'observaciones': item.get('observaciones', ''),
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error procesando item de gasto: {e}")
                    continue
        
        # Forma de pago
        forma_pago = "No especificada"
        if obj.formaPago and hasattr(obj.formaPago, 'formaPago'):
            forma_pago = obj.formaPago.formaPago
        
        # Datos de transferencia
        datos_transferencia = {}
        if obj.datos_forma_pago and isinstance(obj.datos_forma_pago, dict):
            datos_transferencia = obj.datos_forma_pago
        
        # Validaciones con datos correctos de responsables
        responsable_nombre = "No asignado"
        if obj.responsable:
            responsable_parts = []
            if obj.responsable.nombre:
                responsable_parts.append(obj.responsable.nombre)
            if obj.responsable.paterno:
                responsable_parts.append(obj.responsable.paterno)
            if obj.responsable.materno:
                responsable_parts.append(obj.responsable.materno)
            responsable_nombre = " ".join(responsable_parts) if responsable_parts else "No asignado"
        
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
            'numero_formulario': obj.numeroFormulario or f"SV-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'tipo_documento': 'SOLICITUD DE VIAJE - TAREA',
            'subtipo_documento': 'SV-T',
            
            # Datos del USUARIO (solicitante)
            'solicitante': usuario_data,
            
            # Datos de la tarea
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
            'fecha_solicitud': fecha_solicitud,
            'monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else 0.00,
            'forma_pago': forma_pago,
            'datos_transferencia': datos_transferencia,
            
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
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF para solicitudes de viaje de tareas
        """
        numero = obj.numeroFormulario or f"SV-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            # Tomar el primer nombre
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        
        return f"Solicitud_Viaje_Tarea_{nombre_solicitante}_{numero}.pdf"
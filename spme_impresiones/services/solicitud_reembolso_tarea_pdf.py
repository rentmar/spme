from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudReembolso

class SolicitudReembolsoTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Reembolso (exclusivo para Tareas)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_reembolso_tarea_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Reembolso de Tarea
        """
        if not isinstance(obj, SolicitudReembolso):
            raise ValueError("El objeto debe ser una instancia de SolicitudReembolso")
        
        # Formatear fechas
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
        fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada"
        
        # Obtener datos del USUARIO (solicitante) con campos CORRECTOS
        usuario_data = {}
        if obj.usuario:
            # Construir nombre completo usando los campos correctos
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
        
        # Obtener datos de actividad si existe
        actividad_data = {}
        if obj.actividad:
            actividad_data = {
                'codigo': obj.actividad.codigo or "No asignado",
                'nombre': obj.actividad.nombreCorto or obj.actividad.nombreLargo or "Sin nombre",
            }
        
        # Procesar detalle de fondos - ¡ESTRUCTURA CORRECTA!
        detalle_fondos = []
        total_calculado = 0.0
        
        if obj.detalleDestinoFondos and isinstance(obj.detalleDestinoFondos, dict):
            # La estructura es: {"items": [{...}, {...}]}
            items = obj.detalleDestinoFondos.get('items', [])
            
            for item in items:
                try:
                    # Formatear fecha del item
                    fecha_item = item.get('fecha', '')
                    if fecha_item:
                        try:
                            from datetime import datetime
                            fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                            fecha_item = fecha_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            fecha_item = fecha_item  # Mantener como está si hay error
                    
                    monto = float(item.get('monto', 0))
                    total_calculado += monto
                    
                    detalle_fondos.append({
                        'fecha': fecha_item,
                        'partida': item.get('partida', ''),
                        'factura_recibo': item.get('factura_recibo', ''),
                        'concepto': item.get('concepto', ''),
                        'monto': monto,
                        # Campo adicional si existe
                        'observaciones': item.get('observaciones', ''),
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error procesando item: {e}")
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
            'numero_formulario': obj.numeroFormulario or f"SR-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'tipo_documento': 'SOLICITUD DE REEMBOLSO - TAREA',
            'subtipo_documento': 'SR-T',
            
            # Datos del USUARIO (solicitante)
            'solicitante': usuario_data,
            
            # Datos de la tarea
            'tarea': tarea_data,
            
            # Datos de la actividad
            'actividad': actividad_data,
            
            # Datos específicos del reembolso
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
            'responsable_nombre': responsable_nombre,
            'validacion_coordinador': obj.validacionCoordinador,
            'coordinador_nombre': coordinador_nombre,
            
            # Bloqueo de iconos
            'bloqueo_iconos': obj.bloquearIconos,
            
            # Información adicional para debugging
            'estructura_detalle': type(obj.detalleDestinoFondos).__name__,
            'detalle_vacio': not bool(obj.detalleDestinoFondos),
        }
        
        return context
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF para reembolsos de tareas
        """
        numero = obj.numeroFormulario or f"SR-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            # Tomar el primer nombre
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        
        return f"Reembolso_Tarea_{nombre_solicitante}_{numero}.pdf"
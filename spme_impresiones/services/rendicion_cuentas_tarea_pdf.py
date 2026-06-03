from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import RendicionCuentas

class RendicionCuentasTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Rendición de Cuentas (exclusivo para Tareas)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_cuentas_tarea_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Rendición de Cuentas de Tarea
        """
        if not isinstance(obj, RendicionCuentas):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentas")
        
        # Formatear fechas
        fecha_desembolso = obj.fechaDesembolso.strftime('%d/%m/%Y') if obj.fechaDesembolso else "No especificada"
        fecha_actividad = obj.fechaActividad.strftime('%d/%m/%Y') if obj.fechaActividad else "No especificada"
        fecha_rendicion = obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada"
        
        # Obtener datos del USUARIO (responsable de rendición)
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
        
        # Determinar tipo de solicitud relacionada
        tipo_solicitud = "No especificada"
        solicitud_numero = "No especificado"
        
        if obj.solicitudFondos:
            tipo_solicitud = "Solicitud de Fondos"
            solicitud_numero = obj.solicitudFondos.numeroFormulario or f"SF-{obj.solicitudFondos.id}"
        elif obj.solicitudReembolso:
            tipo_solicitud = "Solicitud de Reembolso"
            solicitud_numero = obj.solicitudReembolso.numeroFormulario or f"SR-{obj.solicitudReembolso.id}"
        elif obj.solicitudViaje:
            tipo_solicitud = "Solicitud de Viaje"
            solicitud_numero = obj.solicitudViaje.numeroFormulario or f"SV-{obj.solicitudViaje.id}"
        elif obj.solicitudPagoDirecto:
            tipo_solicitud = "Solicitud de Pago Directo"
            solicitud_numero = obj.solicitudPagoDirecto.numeroFormulario or f"SPD-{obj.solicitudPagoDirecto.id}"
        
        # Procesar detalle de destino de fondos - ¡ESTRUCTURA DIRECTA!
        detalle_fondos = []
        total_calculado = 0.0
        
        if obj.detalleDestinoFondos and isinstance(obj.detalleDestinoFondos, list):
            # La estructura es directamente una lista: [{...}, {...}]
            for index, item in enumerate(obj.detalleDestinoFondos, 1):
                try:
                    # Formatear fecha del item
                    fecha_item = item.get('fecha', '')
                    if fecha_item:
                        try:
                            from datetime import datetime
                            fecha_obj = datetime.strptime(fecha_item, '%Y-%m-%d')
                            fecha_item = fecha_obj.strftime('%d/%m/%Y')
                        except ValueError:
                            fecha_item = fecha_item  # Mantener como está
                    
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

                    factura_recibo = (
                        item.get('factura_recibo') or 
                        item.get('factura') or 
                        item.get('recibo') or 
                        ''
                    )

                    descripcion = (
                        item.get('descripcion') or 
                        item.get('concepto') or 
                        item.get('descripcionGasto') or 
                        ''
                    )
                    
                    monto = float(item.get('monto', 0))
                    total_calculado += monto
                    
                    detalle_fondos.append({
                        'numero': index,
                        'fecha': fecha_item,
                        'partida': item.get('partida', ''),
                        'fuente': str(fuente),
                        'factura_recibo': item.get('factura_recibo', ''),
                        'descripcion': item.get('descripcion', ''),
                        'monto': monto,
                        'observaciones': item.get('observaciones', ''),
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error procesando item de rendición: {e}")
                    continue
        
        # Cálculo de saldo si no está definido
        saldo = float(obj.saldo) if obj.saldo else 0.0
        monto_asignado = float(obj.montoAsignado) if obj.montoAsignado else 0.0
        monto_descargado = float(obj.montoDescargado) if obj.montoDescargado else 0.0
        
        # Si el saldo no está calculado, calcularlo
        if saldo == 0 and monto_asignado > 0 and monto_descargado > 0:
            saldo = monto_asignado - monto_descargado
        
        # Validaciones con datos correctos
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
        
        administrador_nombre = "No asignado"
        if obj.administrador:
            administrador_parts = []
            if obj.administrador.nombre:
                administrador_parts.append(obj.administrador.nombre)
            if obj.administrador.paterno:
                administrador_parts.append(obj.administrador.paterno)
            if obj.administrador.materno:
                administrador_parts.append(obj.administrador.materno)
            administrador_nombre = " ".join(administrador_parts) if administrador_parts else "No asignado"
        
        context = {
            # Datos básicos del formulario
            'numero_formulario': obj.numeroFormulario or f"RC-{obj.id:04d}",
            'fecha_emision': fecha_rendicion,
            'tipo_documento': 'RENDICIÓN DE CUENTAS - SUBACTIVIDAD',
            'subtipo_documento': 'RC-T',
            'cpte_diario': obj.cpteDiario or "No especificado",
            
            # Datos del USUARIO (responsable)
            'responsable_rendicion': usuario_data,
            
            # Datos de la tarea
            'tarea': tarea_data,
            
            # Información financiera
            'fecha_desembolso': fecha_desembolso,
            'fecha_actividad': fecha_actividad,
            'fecha_rendicion': fecha_rendicion,
            'monto_asignado': monto_asignado,
            'monto_descargado': monto_descargado,
            'saldo': saldo,
            'total_calculado': total_calculado,
            
            # Información de actividad
            'descripcion_actividad': obj.descripcionActividad or "No especificada",
            'lugar_actividad': obj.lugarActividad or "No especificado",
            'lugar_rendicion': obj.lugarRendicion or "No especificado",
            
            # Solicitud relacionada
            'tipo_solicitud': tipo_solicitud,
            'solicitud_numero': solicitud_numero,
            
            # Detalle de fondos - ESTRUCTURA DIRECTA
            'detalle_fondos': detalle_fondos,
            'tiene_detalle': len(detalle_fondos) > 0,
            'cantidad_items': len(detalle_fondos),
            
            # Validaciones (4 niveles)
            'validacion_responsable': obj.validacionResponsable,
            'responsable_nombre': responsable_nombre,
            'validacion_coordinador': obj.validacionCoordinador,
            'coordinador_nombre': coordinador_nombre,
            'validacion_contador': obj.validacionContador,
            'contador_nombre': contador_nombre,
            'validacion_administrador': obj.validacionAdministrador,
            'administrador_nombre': administrador_nombre,
            
            # Bloqueo de iconos
            'bloqueo_iconos': obj.bloquearIconos,
            
            # Cálculos y verificaciones
            'diferencia_descargado': abs(monto_descargado - total_calculado) if monto_descargado > 0 else 0,
            'coincide_descargado': abs(monto_descargado - total_calculado) < 0.01,  # Tolerancia de 0.01
            'tiene_saldo': saldo > 0,
        }
        
        return context
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF para rendición de cuentas de tareas
        """
        numero = obj.numeroFormulario or f"RC-{obj.id:04d}"
        nombre_responsable = "responsable"
        if obj.usuario and obj.usuario.nombre:
            # Tomar el primer nombre
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_responsable = nombre_parts[0].lower()
        
        return f"Rendicion_Cuentas_Tarea_{nombre_responsable}_{numero}.pdf"
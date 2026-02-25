# services/solicitud_pago_directo_tarea_pei_pdf.py
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudPagoDirectoActPei
from spme_estructuracion_pei.models import TareaActividadPei
import json

class SolicitudPagoDirectoTareaPeiPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Pago Directo de Tarea PEI
    Para solicitudes que tienen tarea asociada (obj.tarea existe)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_pago_directo_tarea_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para SolicitudPagoDirectoActPei con tarea
        """
        if not isinstance(obj, SolicitudPagoDirectoActPei):
            raise ValueError("El objeto debe ser una instancia de SolicitudPagoDirectoActPei")
        
        # Validar que tenga tarea
        if not obj.tarea:
            raise ValueError("Este generador es solo para solicitudes con tarea")
        
        # Procesar detalle de pagos y obtener total
        detalle_pagos, total_pagos_calculado = self._procesar_detalle_pagos(obj)
        
        # Usar monto solicitado del objeto o calcularlo
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_pagos_calculado
        
        # Obtener actividad y tarea
        actividad = obj.actividad
        tarea = obj.tarea
        
        # Mapeo de estados para tarea
        estados_tarea_map = dict(TareaActividadPei.ESTADOS_TAREA)
        
        # Forma de pago
        forma_pago_texto = obj.formaPago.formaPago if obj.formaPago else "No especificada"
        
        # Crear un concepto/resumen desde el detalle de pagos
        concepto_general = "Pago directo a tercero"
        if detalle_pagos:
            primeros = detalle_pagos[:2]
            concepto_general = ", ".join([p['concepto'] for p in primeros])
            if len(detalle_pagos) > 2:
                concepto_general += f" y {len(detalle_pagos)-2} más"
        
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"PD-TAREA-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            
            # Información del solicitante
            'nombre_solicitante': self._get_nombre_completo_solicitante(obj),
            'documento_identidad': self._get_documento_identidad(obj),
            'cargo': self._get_cargo(obj),
            
            # Información del beneficiario (tercero)
            'nombre_beneficiario': self._get_nombre_beneficiario(obj),
            'documento_beneficiario': self._get_documento_beneficiario(obj),
            'direccion_beneficiario': self._get_direccion_beneficiario(obj),
            'telefono_beneficiario': self._get_telefono_beneficiario(obj),
            'email_beneficiario': self._get_email_beneficiario(obj),
            
            # Información de la TAREA
            'codigo_tarea': tarea.codigo if tarea else "No asignado",
            'titulo_tarea': tarea.titulo if tarea else "No especificado",
            'estado_tarea': estados_tarea_map.get(tarea.estado, tarea.estado) if tarea and tarea.estado else "N/A",
            'fecha_ejecucion_tarea': tarea.fecha_ejecucion.strftime('%d/%m/%Y') if tarea and tarea.fecha_ejecucion else "No especificada",
            'fecha_limite_tarea': tarea.fecha_limite.strftime('%d/%m/%Y') if tarea and tarea.fecha_limite else "No especificada",
            'descripcion_tarea': tarea.descripcion or "No especificada",
            'presupuesto_tarea': float(tarea.presupuesto) if tarea and tarea.presupuesto else 0,
            
            # Información de la ACTIVIDAD (contexto)
            'codigo_actividad': actividad.codigo if actividad else "N/A",
            'nombre_actividad': actividad.nombreCorto if actividad else "No especificado",
            
            # Información del pago - CAMPOS CORREGIDOS
            'concepto_pago': concepto_general,
            'descripcion_actividad': obj.descripcion_actividad or "No especificado",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'forma_pago': forma_pago_texto,
            'lugar_pago': obj.lugarSolicitud or "No especificado",
            'fecha_pago': obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada",
            
            # Montos
            'total_monto_solicitado': monto_solicitado,
            'detalle_pagos': detalle_pagos,
            
            # Información bancaria
            'datos_bancarios_beneficiario': self._get_datos_bancarios_beneficiario(obj),
            
            # Información de validaciones
            'nombre_contador': self._get_nombre_contador(obj),
            'nombre_coordinador': self._get_nombre_coordinador(obj),
            
            # Observaciones (vacío por ahora)
            'observaciones': "",
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE PAGO DIRECTO',
            'subtipo_documento': 'Tarea PEI',
            
            # Flags para template
            'es_tarea': True,
            'tiene_tarea': True,
            'tiene_actividad': bool(actividad),
        }
        
        # Procesar datos de transferencia
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj, forma_pago_texto)
        
        # Procesar documentos adjuntos
        context['documentos_adjuntos'] = self._procesar_documentos_adjuntos(obj)
        
        return context
    
    def _get_nombre_completo_solicitante(self, obj):
        """Obtiene el nombre completo del solicitante"""
        if obj.usuario:
            if hasattr(obj.usuario, 'get_full_name'):
                nombre = obj.usuario.get_full_name()
                if nombre and nombre.strip():
                    return nombre
            
            partes = []
            if obj.usuario.nombre:
                partes.append(obj.usuario.nombre)
            if obj.usuario.paterno:
                partes.append(obj.usuario.paterno)
            if obj.usuario.materno:
                partes.append(obj.usuario.materno)
            
            if partes:
                return " ".join(partes)
            return str(obj.usuario)
        
        return "No asignado"
    
    def _get_documento_identidad(self, obj):
        """Obtiene el documento de identidad del solicitante"""
        if obj.usuario:
            return obj.usuario.ci or "No asignado"
        return "No asignado"
    
    def _get_cargo(self, obj):
        """Obtiene el cargo del solicitante"""
        if obj.usuario:
            return obj.usuario.cargo or "No asignado"
        return "No asignado"
    
    def _get_nombre_beneficiario(self, obj):
        """Obtiene el nombre del beneficiario desde datos_forma_pago"""
        if obj.datos_forma_pago:
            if isinstance(obj.datos_forma_pago, dict):
                # Buscar en otros/terceros
                otros = obj.datos_forma_pago.get('otros', {})
                if otros and isinstance(otros, dict):
                    if otros.get('nombre_otros'):
                        return otros.get('nombre_otros')
                
                # Buscar en transferencia
                transferencia = obj.datos_forma_pago.get('transferencia', {})
                if transferencia and isinstance(transferencia, dict):
                    if transferencia.get('nombre_transferencia'):
                        return transferencia.get('nombre_transferencia')
        
        return "No especificado"
    
    def _get_documento_beneficiario(self, obj):
        """Obtiene el documento del beneficiario desde datos_forma_pago"""
        if obj.datos_forma_pago:
            if isinstance(obj.datos_forma_pago, dict):
                otros = obj.datos_forma_pago.get('otros', {})
                if otros and isinstance(otros, dict):
                    if otros.get('ci_otros'):
                        return otros.get('ci_otros')
                
                transferencia = obj.datos_forma_pago.get('transferencia', {})
                if transferencia and isinstance(transferencia, dict):
                    if transferencia.get('ci_transferencia'):
                        return transferencia.get('ci_transferencia')
        
        return "No especificado"
    
    def _get_direccion_beneficiario(self, obj):
        """Obtiene la dirección del beneficiario"""
        # Si no hay campo específico, retornar valor por defecto
        return "No especificada"
    
    def _get_telefono_beneficiario(self, obj):
        """Obtiene el teléfono del beneficiario"""
        return "No especificado"
    
    def _get_email_beneficiario(self, obj):
        """Obtiene el email del beneficiario"""
        return "No especificado"
    
    def _get_nombre_contador(self, obj):
        """Obtiene el nombre del contador"""
        if obj.contador:
            partes = []
            if obj.contador.nombre:
                partes.append(obj.contador.nombre)
            if obj.contador.paterno:
                partes.append(obj.contador.paterno)
            if partes:
                return " ".join(partes)
            return str(obj.contador)
        return "No asignado"
    
    def _get_nombre_coordinador(self, obj):
        """Obtiene el nombre del coordinador"""
        if obj.coordinador:
            partes = []
            if obj.coordinador.nombre:
                partes.append(obj.coordinador.nombre)
            if obj.coordinador.paterno:
                partes.append(obj.coordinador.paterno)
            if partes:
                return " ".join(partes)
            return str(obj.coordinador)
        return "No asignado"
    
    def _get_datos_bancarios_beneficiario(self, obj):
        """Obtiene datos bancarios desde datos_forma_pago"""
        datos = {
            'banco': '',
            'numero_cuenta': '',
            'tipo_cuenta': '',
            'titular': self._get_nombre_beneficiario(obj),
        }
        
        if obj.datos_forma_pago and isinstance(obj.datos_forma_pago, dict):
            transferencia = obj.datos_forma_pago.get('transferencia', {})
            if transferencia and isinstance(transferencia, dict):
                datos['banco'] = transferencia.get('entidad_bancaria', '')
                datos['numero_cuenta'] = transferencia.get('numero_cuenta', '')
                datos['tipo_cuenta'] = transferencia.get('tipo_cuenta', '')
        
        return datos
    
    def _procesar_detalle_pagos(self, obj):
        """
        Procesa el detalle de pagos del JSON detalleDestinoFondos
        """
        detalle_pagos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            # Si no hay detalle, crear un item con el monto total
            if obj.montoSolicitado:
                detalle_pagos.append({
                    'indice': 1,
                    'concepto': 'Pago directo',
                    'monto': float(obj.montoSolicitado),
                    'observaciones': '-',
                })
                total_monto = float(obj.montoSolicitado)
            return detalle_pagos, total_monto
        
        try:
            data = obj.detalleDestinoFondos
            
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return detalle_pagos, total_monto
            
            items_list = []
            if isinstance(data, dict):
                items_list = data.get('items', data.get('pagos', data.get('detalle', [])))
            elif isinstance(data, list):
                items_list = data
            
            for idx, item in enumerate(items_list, 1):
                if not isinstance(item, dict):
                    continue
                
                concepto = (
                    item.get('concepto') or 
                    item.get('descripcion') or 
                    item.get('motivo') or 
                    f"Pago {idx}"
                )
                
                monto_raw = item.get('monto', item.get('valor', item.get('importe', 0)))
                try:
                    monto = float(monto_raw)
                    total_monto += monto
                except (ValueError, TypeError):
                    monto = 0.0
                
                observaciones = item.get('observaciones', item.get('obs', '-'))
                
                detalle_pagos.append({
                    'indice': idx,
                    'concepto': str(concepto),
                    'monto': monto,
                    'observaciones': str(observaciones),
                })
            
        except Exception as e:
            print(f"Error en _procesar_detalle_pagos: {e}")
        
        return detalle_pagos, total_monto
    
    def _procesar_datos_transferencia(self, obj, forma_pago_texto):
        """Procesa los datos de transferencia bancaria"""
        datos = {
            'mostrar_transferencia': False,
            'banco': '',
            'numero_cuenta': '',
            'tipo_cuenta': '',
            'titular': '',
            'ci_titular': '',
        }
        
        # Verificar si es transferencia
        if 'transferencia' in forma_pago_texto.lower() or 'banco' in forma_pago_texto.lower():
            datos['mostrar_transferencia'] = True
            datos['titular'] = self._get_nombre_beneficiario(obj)
            datos['ci_titular'] = self._get_documento_beneficiario(obj)
            
            # Datos bancarios del formulario
            if obj.datos_forma_pago and isinstance(obj.datos_forma_pago, dict):
                transferencia = obj.datos_forma_pago.get('transferencia', {})
                if transferencia and isinstance(transferencia, dict):
                    datos['banco'] = transferencia.get('entidad_bancaria', '')
                    datos['numero_cuenta'] = transferencia.get('numero_cuenta', '')
                    datos['tipo_cuenta'] = transferencia.get('tipo_cuenta', '')
            
            # Si no hay datos específicos, usar los del beneficiario
            if not datos['banco']:
                db = self._get_datos_bancarios_beneficiario(obj)
                datos['banco'] = db.get('banco', '')
                datos['numero_cuenta'] = db.get('numero_cuenta', '')
                datos['tipo_cuenta'] = db.get('tipo_cuenta', '')
        
        return datos
    
    def _procesar_documentos_adjuntos(self, obj):
        """Procesa documentos adjuntos si existen"""
        # Por ahora retornar lista vacía
        # Si en el futuro hay un campo para documentos, se puede implementar
        return []
    
    def generate_filename(self, obj):
        """Genera el nombre del archivo PDF"""
        numero = obj.numeroFormulario or f"PD-TAREA-{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Pago_Directo_Tarea_PEI_{numero_limpio}.pdf"
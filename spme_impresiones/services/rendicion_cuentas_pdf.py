from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso, 
    SolicitudViaje, 
    SolicitudPagoDirecto,
    RendicionCuentas,
)
from decimal import Decimal

class RendicionCuentasPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Rendición de Cuentas
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_cuentas_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Rendición de Cuentas
        """
        if not isinstance(obj, RendicionCuentas):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentas")
        
        # Determinar la solicitud origen
        solicitud_origen = None
        tipo_solicitud = None
        origen_numero = "No aplica"
        
        if obj.solicitudFondos:
            solicitud_origen = obj.solicitudFondos
            tipo_solicitud = 'SOLICITUD DE FONDOS'
            origen_numero = obj.solicitudFondos.numeroFormulario if obj.solicitudFondos.numeroFormulario else "Sin número"
        elif obj.solicitudReembolso:
            solicitud_origen = obj.solicitudReembolso
            tipo_solicitud = 'SOLICITUD DE REEMBOLSO'
            origen_numero = obj.solicitudReembolso.numeroFormulario if obj.solicitudReembolso.numeroFormulario else "Sin número"
        elif obj.solicitudViaje:
            solicitud_origen = obj.solicitudViaje
            tipo_solicitud = 'SOLICITUD DE VIAJE'
            origen_numero = obj.solicitudViaje.numeroFormulario if obj.solicitudViaje.numeroFormulario else "Sin número"
        elif obj.solicitudPagoDirecto:
            solicitud_origen = obj.solicitudPagoDirecto
            tipo_solicitud = 'SOLICITUD DE PAGO DIRECTO'
            origen_numero = obj.solicitudPagoDirecto.numeroFormulario if obj.solicitudPagoDirecto.numeroFormulario else "Sin número"
        
        # Información del usuario (responsable de rendición)
        nombre_solicitante = ""
        documento_identidad = ""
        cargo = ""
        
        if obj.usuario:
            nombre_solicitante = f"{obj.usuario.nombre} {obj.usuario.paterno}"
            if obj.usuario.materno:
                nombre_solicitante += f" {obj.usuario.materno}"
            documento_identidad = obj.usuario.ci or ""
            cargo = obj.usuario.cargo or ""
        
        # Obtener información de validaciones
        responsables_validacion = self._get_responsables_validacion(obj)
        
        # Calcular saldo
        monto_asignado = obj.montoAsignado or Decimal('0.00')
        monto_descargado = obj.montoDescargado or Decimal('0.00')
        saldo = monto_asignado - monto_descargado
        
        # Procesar detalle de gastos
        detalle_gastos = self._procesar_detalle_gastos(obj)
        
        # Determinar estado general basado en validaciones
        estado = self._determinar_estado(obj)
        
        context = {
            # Información básica
            'numero_formulario': obj.numeroFormulario or "No asignado",
            'cpte_diario': obj.cpteDiario or "No asignado",
            'fecha_rendicion': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada",
            'fecha_desembolso': obj.fechaDesembolso.strftime('%d/%m/%Y') if obj.fechaDesembolso else "No especificada",
            'fecha_actividad': obj.fechaActividad.strftime('%d/%m/%Y') if obj.fechaActividad else "No especificada",
            
            # Información del responsable de rendición
            'nombre_solicitante': nombre_solicitante,
            'documento_identidad': documento_identidad,
            'cargo': cargo,
            
            # Información de la actividad
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'descripcion_actividad': obj.descripcionActividad or "No especificada",
            'lugar_actividad': obj.lugarActividad or "No especificado",
            'lugar_rendicion': obj.lugarRendicion or "No especificado",
            'nombre_tarea': obj.tarea.nombreTarea if obj.tarea else "No especificado",
            
            # Información financiera
            'monto_asignado': float(monto_asignado),
            'monto_descargado': float(monto_descargado),
            'saldo': float(saldo),
            'saldo_absoluto': float(abs(saldo)),
            'saldo_formateado': f"Bs. {saldo:,.2f}",
            'tiene_saldo_favor': saldo > 0,
            'tiene_saldo_debito': saldo < 0,
            'monto_asignado_formateado': f"Bs. {monto_asignado:,.2f}",
            'monto_descargado_formateado': f"Bs. {monto_descargado:,.2f}",
            
            # Información de solicitud origen
            'solicitud_origen_numero': origen_numero,
            'tipo_solicitud_origen': tipo_solicitud or "No aplica",
            
            # Validaciones
            'responsables_validacion': responsables_validacion,
            'validacion_responsable': obj.validacionResponsable,
            'validacion_coordinador': obj.validacionCoordinador,
            'validacion_contador': obj.validacionContador,
            'validacion_administrador': obj.validacionAdministrador,
            
            # Detalle
            'detalle_gastos': detalle_gastos,
            'cantidad_gastos': len(detalle_gastos),
            'tiene_gastos': len(detalle_gastos) > 0,
            
            # Estado y tipo de documento
            'estado': estado,
            'estado_color': self._get_color_estado(estado),
            'tipo_documento': 'RENDICIÓN DE CUENTAS',
            'subtipo_documento': 'F-05',
            
            # Información de validadores
            'nombre_contador': self._get_nombre_completo(obj.contador) if obj.contador else "No asignado",
            'nombre_coordinador': self._get_nombre_completo(obj.coordinador) if obj.coordinador else "No asignado",
            'nombre_administrador': self._get_nombre_completo(obj.administrador) if obj.administrador else "No asignado",
            'nombre_responsable': self._get_nombre_completo(obj.responsable) if obj.responsable else "No asignado",
            
            # Campos adicionales útiles
            'bloqueado': obj.bloquearIconos,
            'es_completo': all([
                obj.validacionResponsable,
                obj.validacionCoordinador,
                obj.validacionContador,
                obj.validacionAdministrador
            ])
        }
        
        return context
    
    def _get_nombre_completo(self, usuario):
        """
        Obtiene el nombre completo de un usuario
        """
        if not usuario:
            return ""
        
        nombre_completo = f"{usuario.nombre} {usuario.paterno}"
        if usuario.materno:
            nombre_completo += f" {usuario.materno}"
        
        return nombre_completo.strip()
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del JSONField
        """
        detalle_gastos = []
        
        if obj.detalleDestinoFondos:
            # Si es una lista de diccionarios
            if isinstance(obj.detalleDestinoFondos, list):
                for item in obj.detalleDestinoFondos:
                    if isinstance(item, dict):
                        gasto = self._procesar_item_gasto(item)
                        if gasto:
                            detalle_gastos.append(gasto)
            # Si es un diccionario individual
            elif isinstance(obj.detalleDestinoFondos, dict):
                gasto = self._procesar_item_gasto(obj.detalleDestinoFondos)
                if gasto:
                    detalle_gastos.append(gasto)
        
        return detalle_gastos
        
    def _procesar_item_gasto(self, item):
        """
        Procesa un item individual de gasto
        """
        try:
            # Obtener valores con claves alternativas
            partida = item.get('partida') or item.get('partidaPresupuestaria') or item.get('partidaCodigo') or '-'

            fuente = (
                item.get('fuente') or 
                item.get('fuente_financiamiento') or 
                item.get('fuente_fin') or 
                item.get('origen') or 
                'No especificada'
            )
            
            descripcion = item.get('descripcionGasto') or item.get('descripcion') or item.get('concepto') or '-'
            
            fecha_gasto = item.get('fechaGasto') or item.get('fecha') or item.get('fechaComprobante')
            
            # ===== CORREGIDO: Usar factura_recibo en lugar de numero_comprobante =====
            factura_recibo = item.get('factura_recibo') or item.get('numeroComprobante') or item.get('comprobante') or item.get('numeroFactura') or '-'
            # =========================================================================
            
            monto = item.get('monto') or item.get('valor') or item.get('importe') or 0
            try:
                monto_float = float(monto)
            except:
                monto_float = 0.0
            
            observaciones = item.get('observaciones') or item.get('notas') or '-'
            
            tipo_comprobante = item.get('tipoComprobante') or item.get('tipoDocumento') or item.get('documento') or '-'
            
            proveedor = item.get('proveedor') or item.get('beneficiario') or item.get('nombreProveedor') or '-'
            
            verificado = item.get('verificado', False) or item.get('validado', False) or False
            
            gasto = {
                'partida': partida,
                'fuente': fuente,   
                'descripcion_gasto': descripcion,
                'fecha_gasto': fecha_gasto,
                'factura_recibo': factura_recibo,  # CAMBIADO de numero_comprobante a factura_recibo
                'monto': monto_float,
                'observaciones': observaciones,
                'verificado': verificado,
                'tipo_comprobante': tipo_comprobante,
                'proveedor': proveedor
            }
            
            # Formatear fecha si existe
            if gasto['fecha_gasto'] and gasto['fecha_gasto'] != '-':
                try:
                    from datetime import datetime
                    # Intentar diferentes formatos de fecha
                    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
                    fecha_obj = None
                    
                    for formato in formatos:
                        try:
                            fecha_obj = datetime.strptime(str(gasto['fecha_gasto']), formato)
                            break
                        except:
                            continue
                    
                    if fecha_obj:
                        gasto['fecha_gasto_formateada'] = fecha_obj.strftime('%d/%m/%Y')
                    else:
                        gasto['fecha_gasto_formateada'] = str(gasto['fecha_gasto'])
                except Exception as e:
                    print(f"Error formateando fecha: {e}")
                    gasto['fecha_gasto_formateada'] = str(gasto['fecha_gasto'])
            else:
                gasto['fecha_gasto_formateada'] = '-'
            
            # Formatear monto
            gasto['monto_formateado'] = f"Bs. {monto_float:,.2f}"
            
            return gasto
            
        except Exception as e:
            print(f"Error procesando item de gasto: {e}")
            return None
    
    def _get_responsables_validacion(self, obj):
        """
        Obtiene información de los responsables de validación
        (Solo Coordinador, Contador, Administrador)
        """
        responsables = []
        
        # Coordinador
        if obj.coordinador:
            responsables.append({
                'nombre': self._get_nombre_completo(obj.coordinador),
                'cargo': obj.coordinador.cargo or "Coordinador",
                'validado': obj.validacionCoordinador,
                'fecha': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "-",
                'icono': '✓' if obj.validacionCoordinador else '✗',
                'color': 'success' if obj.validacionCoordinador else 'danger',
                'ci': obj.coordinador.ci or ""
            })
        
        # Contador
        if obj.contador:
            responsables.append({
                'nombre': self._get_nombre_completo(obj.contador),
                'cargo': obj.contador.cargo or "Contador",
                'validado': obj.validacionContador,
                'fecha': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "-",
                'icono': '✓' if obj.validacionContador else '✗',
                'color': 'success' if obj.validacionContador else 'danger',
                'ci': obj.contador.ci or ""
            })
        
        # Administrador
        if obj.administrador:
            responsables.append({
                'nombre': self._get_nombre_completo(obj.administrador),
                'cargo': obj.administrador.cargo or "Administrador",
                'validado': obj.validacionAdministrador,
                'fecha': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "-",
                'icono': '✓' if obj.validacionAdministrador else '✗',
                'color': 'success' if obj.validacionAdministrador else 'danger',
                'ci': obj.administrador.ci or ""
            })
        
        return responsables
    
    def _determinar_estado(self, obj):
        """
        Determina el estado de la rendición basado en las validaciones
        """
        if obj.validacionAdministrador:
            return "APROBADO"
        elif obj.validacionContador:
            return "VERIFICADO"
        elif obj.validacionCoordinador:
            return "REVISADO"
        elif obj.validacionResponsable:
            return "EN REVISIÓN"
        else:
            return "PENDIENTE"
    
    def _get_color_estado(self, estado):
        """
        Retorna el color correspondiente al estado
        """
        colores = {
            'APROBADO': '#2e7d32',      # Verde
            'VERIFICADO': '#0288d1',    # Azul
            'REVISADO': '#f57c00',      # Naranja
            'EN REVISIÓN': '#ff9800',   # Naranja claro
            'PENDIENTE': '#d32f2f',     # Rojo
        }
        return colores.get(estado, '#666666')
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF específico para Rendición de Cuentas
        """
        if self.filename:
            return self.filename
            
        if obj.numeroFormulario:
            # Limpiar caracteres no válidos para nombre de archivo
            numero_limpio = obj.numeroFormulario.replace('/', '_').replace('\\', '_')
            return f"Rendicion_Cuentas_{numero_limpio}.pdf"
        else:
            return f"Rendicion_Cuentas_{obj.id:04d}.pdf"
# spme_impresiones/pdf_generators/rendicion_cuentas.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import (
    SolicitudFondos,
    SolicitudReembolso,
    SolicitudViaje,
    SolicitudPagoDirecto,
    RendicionCuentas,
)
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService
from decimal import Decimal


class RendicionCuentasPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Rendición de Cuentas
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_cuentas_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        if not isinstance(obj, RendicionCuentas):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentas")
        
        # Determinar la solicitud origen
        solicitud_origen = None
        tipo_solicitud = None
        origen_numero = "No aplica"
        
        if obj.solicitudFondos:
            tipo_solicitud = 'SOLICITUD DE FONDOS'
            origen_numero = obj.solicitudFondos.numeroFormulario or "Sin número"
        elif obj.solicitudReembolso:
            tipo_solicitud = 'SOLICITUD DE REEMBOLSO'
            origen_numero = obj.solicitudReembolso.numeroFormulario or "Sin número"
        elif obj.solicitudViaje:
            tipo_solicitud = 'SOLICITUD DE VIAJE'
            origen_numero = obj.solicitudViaje.numeroFormulario or "Sin número"
        elif obj.solicitudPagoDirecto:
            tipo_solicitud = 'SOLICITUD DE PAGO DIRECTO'
            origen_numero = obj.solicitudPagoDirecto.numeroFormulario or "Sin número"
        
        # Obtener validadores del servicio
        if self.USAR_ETIQUETAS_GENERICAS:
            validadores = self.validacion_service.obtener_validadores(obj, self.etiquetas_revisor)
        else:
            validadores = self.validacion_service.obtener_validadores(obj)
        
        solicitante = self.validacion_service.obtener_solicitante(obj)
        estado = self.validacion_service.calcular_estado_documento(validadores)
        
        contexto_validacion = {
            'validadores': validadores,
            'solicitante': solicitante,
            'estado_documento': estado,
            'total_validadores': len(validadores),
            'aprobados': sum(1 for v in validadores if v['estado'] == 'APROBADO'),
            'pendientes': sum(1 for v in validadores if v['estado'] == 'PENDIENTE'),
            'rechazados': sum(1 for v in validadores if v['estado'] == 'RECHAZADO'),
        }
        
        # Calcular saldo
        monto_asignado = obj.montoAsignado or Decimal('0.00')
        monto_descargado = obj.montoDescargado or Decimal('0.00')
        saldo = monto_asignado - monto_descargado
        
        # Procesar detalle de gastos
        detalle_gastos = self._procesar_detalle_gastos(obj)
        
        context = {
            'numero_formulario': obj.numeroFormulario or "No asignado",
            'cpte_diario': obj.cpteDiario or "No asignado",
            'fecha_rendicion': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada",
            'fecha_desembolso': obj.fechaDesembolso.strftime('%d/%m/%Y') if obj.fechaDesembolso else "No especificada",
            'fecha_actividad': obj.fechaActividad.strftime('%d/%m/%Y') if obj.fechaActividad else "No especificada",
            
            'nombre_solicitante': contexto_validacion['solicitante']['nombre'],
            'documento_identidad': contexto_validacion['solicitante']['documento_identidad'],
            'cargo': contexto_validacion['solicitante']['cargo'],
            
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'descripcion_actividad': obj.descripcionActividad or "No especificada",
            'lugar_actividad': obj.lugarActividad or "No especificado",
            'lugar_rendicion': obj.lugarRendicion or "No especificado",
            'nombre_tarea': obj.tarea.nombreTarea if obj.tarea else "No especificado",
            
            'monto_asignado': float(monto_asignado),
            'monto_descargado': float(monto_descargado),
            'saldo': float(saldo),
            'saldo_absoluto': float(abs(saldo)),
            'saldo_formateado': f"Bs. {saldo:,.2f}",
            'tiene_saldo_favor': saldo > 0,
            'tiene_saldo_debito': saldo < 0,
            'monto_asignado_formateado': f"Bs. {monto_asignado:,.2f}",
            'monto_descargado_formateado': f"Bs. {monto_descargado:,.2f}",
            
            'solicitud_origen_numero': origen_numero,
            'tipo_solicitud_origen': tipo_solicitud or "No aplica",
            
            'validadores': contexto_validacion['validadores'],
            'solicitante': contexto_validacion['solicitante'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            'detalle_gastos': detalle_gastos,
            'cantidad_gastos': len(detalle_gastos),
            'tiene_gastos': len(detalle_gastos) > 0,
            
            'tipo_documento': 'RENDICIÓN DE CUENTAS',
            'subtipo_documento': 'F-05',
        }
        
        return context
    
    def _procesar_detalle_gastos(self, obj):
        detalle_gastos = []
        
        if obj.detalleDestinoFondos:
            if isinstance(obj.detalleDestinoFondos, list):
                for item in obj.detalleDestinoFondos:
                    if isinstance(item, dict):
                        gasto = self._procesar_item_gasto(item)
                        if gasto:
                            detalle_gastos.append(gasto)
            elif isinstance(obj.detalleDestinoFondos, dict):
                gasto = self._procesar_item_gasto(obj.detalleDestinoFondos)
                if gasto:
                    detalle_gastos.append(gasto)
        
        return detalle_gastos
    
    def _procesar_item_gasto(self, item):
        try:
            partida = item.get('partida') or item.get('partidaPresupuestaria') or item.get('partidaCodigo') or '-'
            
            fuente_raw = (
                item.get('fuente') or 
                item.get('fuente_financiamiento') or 
                item.get('fuente_fin') or 
                item.get('origen') or 
                'No especificada'
            )
            
            if isinstance(fuente_raw, dict):
                sigla = fuente_raw.get('sigla')
                financiera = fuente_raw.get('financiera')
                fuente = sigla + '-' + financiera
                # fuente = fuente_raw.get('sigla', str(fuente_raw))
            else:
                fuente = str(fuente_raw)
            
            descripcion = item.get('descripcionGasto') or item.get('descripcion') or item.get('concepto') or '-'
            fecha_gasto = item.get('fechaGasto') or item.get('fecha') or item.get('fechaComprobante')
            factura_recibo = item.get('factura_recibo') or item.get('numeroComprobante') or item.get('comprobante') or '-'
            
            monto = item.get('monto') or item.get('valor') or item.get('importe') or 0
            try:
                monto_float = float(monto)
            except:
                monto_float = 0.0
            
            observaciones = item.get('observaciones') or item.get('notas') or '-'
            tipo_comprobante = item.get('tipoComprobante') or item.get('tipoDocumento') or '-'
            proveedor = item.get('proveedor') or item.get('beneficiario') or '-'
            verificado = item.get('verificado', False) or item.get('validado', False) or False
            
            gasto = {
                'partida': partida,
                'fuente': fuente,
                'descripcion_gasto': descripcion,
                'fecha_gasto': fecha_gasto,
                'factura_recibo': factura_recibo,
                'monto': monto_float,
                'observaciones': observaciones,
                'verificado': verificado,
                'tipo_comprobante': tipo_comprobante,
                'proveedor': proveedor,
            }
            
            if gasto['fecha_gasto'] and gasto['fecha_gasto'] != '-':
                try:
                    from datetime import datetime
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
                except:
                    gasto['fecha_gasto_formateada'] = str(gasto['fecha_gasto'])
            else:
                gasto['fecha_gasto_formateada'] = '-'
            
            gasto['monto_formateado'] = f"Bs. {monto_float:,.2f}"
            
            return gasto
            
        except Exception as e:
            print(f"Error procesando item de gasto: {e}")
            return None
    
    def generate_filename(self, obj):
        if self.filename:
            return self.filename
        if obj.numeroFormulario:
            numero_limpio = obj.numeroFormulario.replace('/', '_').replace('\\', '_')
            return f"Rendicion_Cuentas_{numero_limpio}.pdf"
        return f"Rendicion_Cuentas_{obj.id:04d}.pdf"
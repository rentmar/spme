# spme_impresiones/pdf_generators/solicitud_fondos_tarea.py

import json
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudFondos, TareaActividad
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService
from django.utils import timezone


class SolicitudFondosTareaPDFGenerator(BasePDFGenerator):
    """
    Generador ESPECÍFICO para Solicitud de Fondos asociada a una Tarea
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_fondos_tarea_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        if not isinstance(obj, SolicitudFondos):
            raise ValueError("El objeto debe ser una instancia de SolicitudFondos")
        
        if not obj.tarea:
            raise ValueError("Esta solicitud de fondos no tiene una tarea asociada")
        
        tarea = obj.tarea
        
        # Información de la tarea
        codigo_tarea = tarea.codigo if tarea.codigo else "No asignado"
        titulo_tarea = tarea.titulo if tarea.titulo else "Sin título"
        descripcion_tarea = tarea.descripcion if tarea.descripcion else "Sin descripción"
        
        estado_tarea_raw = tarea.estado if tarea.estado else 'PEN'
        estados_dict = dict(TareaActividad.ESTADOS_TAREA)
        estado_tarea_display = estados_dict.get(estado_tarea_raw, estado_tarea_raw)
        
        fecha_ejecucion_tarea = tarea.fecha_ejecucion.strftime('%d/%m/%Y') if tarea.fecha_ejecucion else "No especificada"
        fecha_creacion_tarea = tarea.fecha_creacion.strftime('%d/%m/%Y') if tarea.fecha_creacion else "No especificada"
        fecha_limite_tarea = tarea.fecha_limite.strftime('%d/%m/%Y') if tarea.fecha_limite else "No especificada"
        presupuesto_tarea = float(tarea.presupuesto) if tarea.presupuesto else 0.00
        
        # Información de la actividad padre
        actividad = tarea.actividad if tarea else None
        codigo_actividad = actividad.codigo if actividad else "N/A"
        nombre_actividad = actividad.nombreCorto if actividad else "N/A"
        estado_actividad = actividad.estado if actividad else "N/A"
        
        # Obtener validadores del servicio
        if self.USAR_ETIQUETAS_GENERICAS:
            validadores = self.validacion_service.obtener_validadores(obj, self.etiquetas_revisor)
        else:
            validadores = self.validacion_service.obtener_validadores(obj)
        
        solicitante = self.validacion_service.obtener_solicitante(obj)
        estado_documento = self.validacion_service.calcular_estado_documento(validadores)
        
        contexto_validacion = {
            'validadores': validadores,
            'solicitante': solicitante,
            'estado_documento': estado_documento,
            'total_validadores': len(validadores),
            'aprobados': sum(1 for v in validadores if v['estado'] == 'APROBADO'),
            'pendientes': sum(1 for v in validadores if v['estado'] == 'PENDIENTE'),
            'rechazados': sum(1 for v in validadores if v['estado'] == 'RECHAZADO'),
        }
        
        # Fechas
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else timezone.now().strftime('%d/%m/%Y')
        
        if obj.fechaRealizacionActividad:
            fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y')
        elif tarea and tarea.fecha_ejecucion:
            fecha_realizacion = tarea.fecha_ejecucion.strftime('%d/%m/%Y')
        else:
            fecha_realizacion = "No especificada"
        
        # Procesar detalle de gastos
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        monto_final = float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos_calculado
        
        # Procesar forma de pago
        datos_transferencia = self._procesar_datos_transferencia(obj)
        
        # Cálculos de presupuesto
        diferencia_presupuesto = presupuesto_tarea - monto_final
        dentro_presupuesto = diferencia_presupuesto >= 0
        porcentaje_uso = (monto_final / presupuesto_tarea * 100) if presupuesto_tarea > 0 else 0
        
        context = {
            # Documento
            'tipo_documento': 'SOLICITUD DE FONDOS - TAREA',
            'subtipo_documento': 'F-01-T',
            'numero_formulario': obj.numeroFormulario or f"SF-T-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'fecha_solicitud': fecha_solicitud,
            
            # Tarea
            'codigo_tarea': codigo_tarea,
            'titulo_tarea': titulo_tarea,
            'descripcion_tarea': descripcion_tarea,
            'estado_tarea': estado_tarea_display,
            'estado_tarea_raw': estado_tarea_raw,
            'fecha_ejecucion_tarea': fecha_ejecucion_tarea,
            'fecha_creacion_tarea': fecha_creacion_tarea,
            'fecha_limite_tarea': fecha_limite_tarea,
            'presupuesto_tarea': presupuesto_tarea,
            
            # Actividad padre
            'codigo_actividad': codigo_actividad,
            'nombre_actividad': nombre_actividad,
            'estado_actividad': estado_actividad,
            'tiene_actividad_asociada': bool(actividad),
            
            # Solicitante (desde el servicio)
            'nombre_solicitante': contexto_validacion['solicitante']['nombre'],
            'documento_identidad': contexto_validacion['solicitante']['documento_identidad'],
            'cargo': contexto_validacion['solicitante']['cargo'],
            
            # Solicitud
            'fecha_realizacion': fecha_realizacion,
            'descripcion_actividad': obj.descripcion_actividad or descripcion_tarea,
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'total_monto_solicitado': monto_final,
            
            # Validaciones (NUEVO)
            'validadores': contexto_validacion['validadores'],
            'solicitante': contexto_validacion['solicitante'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            # Forma de pago
            'datos_transferencia': datos_transferencia,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'tiene_detalle_gastos': len(detalle_gastos) > 0,
            
            # Cálculos
            'diferencia_presupuesto': diferencia_presupuesto,
            'dentro_presupuesto': dentro_presupuesto,
            'porcentaje_uso': porcentaje_uso,
        }
        
        return context
    
    def _procesar_datos_transferencia(self, obj):
        datos_forma_pago = {
            'efectivo': {},
            'transferencia': {},
            'cheque': {},
            'otros': {},
            'mostrar_efectivo': False,
            'mostrar_transferencia': False,
            'mostrar_cheque': False,
            'mostrar_otros': False,
            'tipo': None,
        }
        
        if not obj.datos_forma_pago:
            return datos_forma_pago
        
        try:
            if isinstance(obj.datos_forma_pago, dict):
                datos_forma_pago.update(obj.datos_forma_pago)
            elif isinstance(obj.datos_forma_pago, str):
                try:
                    parsed_data = json.loads(obj.datos_forma_pago)
                    datos_forma_pago.update(parsed_data)
                except json.JSONDecodeError:
                    pass
            
            codigo = obj.formaPago.codigo if obj.formaPago else None
            
            mapeo_tipos = {
                'EFEC': 'efectivo',
                'TB': 'transferencia',
                'CHE': 'cheque',
            }
            
            tipo_seleccionado = mapeo_tipos.get(codigo)
            
            if tipo_seleccionado:
                datos_forma_pago['tipo'] = tipo_seleccionado
                datos_forma_pago[f'mostrar_{tipo_seleccionado}'] = True
        
        except Exception as e:
            print(f"Error procesando datos de forma de pago: {e}")
        
        return datos_forma_pago
    
    def _procesar_detalle_gastos(self, obj):
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_gastos, total_monto
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    return detalle_gastos, total_monto
            
            items_list = []
            if isinstance(data_dict, dict) and 'items' in data_dict:
                items_list = data_dict['items']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            for index, item in enumerate(items_list, 1):
                if not isinstance(item, dict):
                    continue
                
                partida = item.get('partida_sf') or item.get('partida') or f"Partida {index}"
                
                fuente_raw = (
                    item.get('fuente') or 
                    item.get('fuente_financiamiento') or 
                    item.get('fuente_fin') or 
                    item.get('origen') or 
                    'No especificada'
                )
                
                if isinstance(fuente_raw, dict):
                    fuente = fuente_raw.get('sigla', str(fuente_raw))
                else:
                    fuente = str(fuente_raw)
                
                concepto = item.get('concepto') or item.get('descripcionGasto') or f"Item {index}"
                
                monto_raw = item.get('monto', 0)
                try:
                    monto = float(monto_raw)
                    total_monto += monto
                except (ValueError, TypeError):
                    monto = 0.0
                
                observaciones = item.get('observaciones', '')
                
                detalle_gastos.append({
                    'numero': index,
                    'partida': str(partida),
                    'fuente': fuente,
                    'descripcion_gasto': str(concepto),
                    'monto': monto,
                    'observaciones': str(observaciones),
                })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos: {e}")
        
        return detalle_gastos, total_monto
    
    def generate_filename(self, obj):
        if self.filename:
            return self.filename
        if obj.tarea and obj.tarea.codigo:
            codigo_limpio = obj.tarea.codigo.replace('/', '-')
            return f"Solicitud_Fondos_Tarea_{codigo_limpio}.pdf"
        elif obj.numeroFormulario:
            return f"Solicitud_Fondos_Tarea_{obj.numeroFormulario}.pdf"
        return f"Solicitud_Fondos_Tarea_ID{obj.id}.pdf"
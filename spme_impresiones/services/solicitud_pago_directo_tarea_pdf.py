# spme_impresiones/pdf_generators/solicitud_pago_directo_tarea.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudPagoDirecto
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService


class SolicitudPagoDirectoTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Pago Directo (exclusivo para Tareas)
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_pago_directo_tarea_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        if not isinstance(obj, SolicitudPagoDirecto):
            raise ValueError("El objeto debe ser una instancia de SolicitudPagoDirecto")
        
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada"
        fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada"
        
        tarea_data = self._get_tarea_data(obj)
        actividad_data = self._get_actividad_data(obj)
        
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
        
        detalle_fondos, total_calculado = self._procesar_detalle_fondos(obj)
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_calculado
        
        datos_transferencia = self._procesar_datos_transferencia(obj)
        
        context = {
            'numero_formulario': obj.numeroFormulario or f"SPD-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'fecha_solicitud': fecha_solicitud,
            'tipo_documento': 'SOLICITUD DE PAGO DIRECTO - TAREA',
            'subtipo_documento': 'SPD-T',
            
            'solicitante': contexto_validacion['solicitante'],
            'tarea': tarea_data,
            'actividad': actividad_data,
            
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'fecha_realizacion': fecha_realizacion,
            'descripcion_actividad': obj.descripcion_actividad or "No especificada",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'monto_solicitado': monto_solicitado,
            
            'validadores': contexto_validacion['validadores'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'datos_transferencia': datos_transferencia,
            
            'detalle_fondos': detalle_fondos,
            'total_calculado': total_calculado,
            'tiene_detalle': len(detalle_fondos) > 0,
            'cantidad_items': len(detalle_fondos),
        }
        
        return context
    
    def _get_tarea_data(self, obj):
        if not obj.tarea:
            return {}
        return {
            'codigo': obj.tarea.codigo or "No asignado",
            'titulo': obj.tarea.titulo or "Sin título",
            'descripcion': obj.tarea.descripcion or "Sin descripción",
            'fecha_creacion': obj.tarea.fecha_creacion.strftime('%d/%m/%Y') if obj.tarea.fecha_creacion else "No especificada",
            'fecha_limite': obj.tarea.fecha_limite.strftime('%d/%m/%Y') if obj.tarea.fecha_limite else "No especificada",
            'estado': obj.tarea.get_estado_display() if hasattr(obj.tarea, 'get_estado_display') else "No especificado",
            'presupuesto': float(obj.tarea.presupuesto) if obj.tarea.presupuesto else 0.0,
        }
    
    def _get_actividad_data(self, obj):
        if not obj.tarea or not obj.tarea.actividad:
            return {}
        actividad = obj.tarea.actividad
        return {
            'codigo': actividad.codigo or "No asignado",
            'nombre_corto': actividad.nombreCorto or "Sin nombre",
        }
    
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
                import json
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
    
    def _procesar_detalle_fondos(self, obj):
        detalle_fondos = []
        total_calculado = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_fondos, total_calculado
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    return detalle_fondos, total_calculado
            
            items = []
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items = data_dict['items']
            elif isinstance(data_dict, list):
                items = data_dict
            
            for index, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    continue
                
                monto = float(item.get('monto', 0))
                total_calculado += monto
                
                partida = item.get('partida_sf') or item.get('partida') or ''
                
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
                
                detalle_fondos.append({
                    'numero': index,
                    'partida_sf': str(partida),
                    'fuente': fuente,
                    'concepto': item.get('concepto', '') or item.get('descripcion', ''),
                    'monto': monto,
                })
        
        except Exception as e:
            print(f"Error procesando detalle de fondos: {e}")
        
        return detalle_fondos, total_calculado
    
    def generate_filename(self, obj):
        numero = obj.numeroFormulario or f"SPD-{obj.id:04d}"
        nombre_solicitante = "solicitante"
        if obj.usuario and obj.usuario.nombre:
            nombre_parts = obj.usuario.nombre.split()
            if nombre_parts:
                nombre_solicitante = nombre_parts[0].lower()
        return f"Pago_Directo_Tarea_{nombre_solicitante}_{numero}.pdf"
# spme_impresiones/pdf_generators/solicitud_fondos.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudFondos
from spme_impresiones.services.validadores_documentos_service import ValidadoresDocumentoService


class SolicitudFondosPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Fondos
    
    Configuración:
        USAR_ETIQUETAS_GENERICAS = True  → Todos los validadores como "REVISOR"
        USAR_ETIQUETAS_GENERICAS = False → Muestra el cargo real (Contable, Coordinador, etc.)
    """
    
    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_fondos_template.html'
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
        
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos_calculado
        
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
        
        context = {
            'numero_formulario': obj.numeroFormulario or f"SF-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            
            'nombre_solicitante': contexto_validacion['solicitante']['nombre'],
            'documento_identidad': contexto_validacion['solicitante']['documento_identidad'],
            'cargo': contexto_validacion['solicitante']['cargo'],
            
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'estado_actividad': self._get_estado_actividad(obj),
            'fecha_ejecucion': obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada",
            'descripcion_actividad': obj.descripcion_actividad or "No especificada",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'total_monto_solicitado': monto_solicitado,
            
            'detalle_gastos': detalle_gastos,
            
            'validadores': contexto_validacion['validadores'],
            'solicitante': contexto_validacion['solicitante'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],
            
            'datos_bancarios_solicitante': self._get_datos_bancarios_solicitante(obj),
            
            'tipo_documento': 'SOLICITUD DE FONDOS',
            'subtipo_documento': 'F-01',
        }
        
        context['fuentes_financiamiento'] = self._procesar_fuentes_financiamiento(obj)
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        
        return context
    
    def _get_estado_actividad(self, obj):
        if obj.actividad and obj.actividad.estado:
            estado = obj.actividad.estado
            estados_map = {
                'CRD': 'Creada', 'PLAN': 'Planificada', 'RETR': 'Retraso',
                'REPROG': 'Reprogramación', 'EJEC': 'En Ejecución',
                'REP': 'En Reporte', 'FIN': 'Finalizado',
            }
            return estados_map.get(estado, estado)
        return "No especificado"
    
    def _get_datos_bancarios_solicitante(self, obj):
        datos = {}
        if obj.usuario:
            datos = {
                'banco': obj.usuario.banco or '',
                'numero_cuenta': obj.usuario.numero_cuenta or '',
                'tipo_cuenta': obj.usuario.tipo_cuenta or '',
                'nombre_completo': obj.usuario.get_full_name() if obj.usuario else '',
                'ci': obj.usuario.ci or '',
            }
        return datos
    
    def _procesar_detalle_gastos(self, obj):
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_gastos, total_monto
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                import json
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    return detalle_gastos, total_monto
            
            items_list = []
            
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items_list = data_dict['items']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            if not isinstance(items_list, list):
                return detalle_gastos, total_monto
            
            for index, item in enumerate(items_list):
                if not isinstance(item, dict):
                    continue
                
                partida = (
                    item.get('partida_sf') or 
                    item.get('partida') or 
                    item.get('codigo') or 
                    f"{index + 1}"
                )

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
                    # fuente = fuente_raw.get('sigla' + 'financiera', str(fuente_raw))
                else:
                    fuente = str(fuente_raw)
                
                concepto = (
                    item.get('concepto') or 
                    item.get('descripcion') or 
                    item.get('descripcionGasto') or 
                    item.get('nombre') or 
                    f"Item {index + 1}"
                )
                
                monto_raw = (
                    item.get('monto') or 
                    item.get('valor') or 
                    item.get('importe') or 
                    item.get('precio') or 
                    0
                )
                
                try:
                    monto = float(monto_raw)
                    total_monto += monto
                except (ValueError, TypeError):
                    monto = 0.0
                
                observaciones = (
                    item.get('observaciones') or 
                    item.get('observacion') or 
                    item.get('notas') or 
                    item.get('comentarios') or 
                    '-'
                )
                
                detalle_gastos.append({
                    'indice': index + 1,
                    'partida': str(partida),
                    'fuente': fuente,
                    'descripcion_gasto': str(concepto),
                    'monto': monto,
                    'observaciones': str(observaciones),
                })
            
        except Exception as e:
            print(f"Error en _procesar_detalle_gastos: {e}")
        
        return detalle_gastos, total_monto
    
    def _procesar_fuentes_financiamiento(self, obj):
        fuentes_financiamiento = []
        if obj.actividad and obj.actividad.procedencia_fondos:
            try:
                if isinstance(obj.actividad.procedencia_fondos, list):
                    for fuente in obj.actividad.procedencia_fondos:
                        if isinstance(fuente, dict):
                            fuentes_financiamiento.append({
                                'nombre': fuente.get('nombre', fuente.get('descripcion', 'Sin nombre')),
                                'monto': float(fuente.get('monto', fuente.get('valor', 0)))
                            })
            except Exception as e:
                print(f"Error procesando fuentes de financiamiento: {e}")
                fuentes_financiamiento = []
        
        return fuentes_financiamiento
    
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
    
    def generate_filename(self, obj):
        numero = obj.numeroFormulario or f"SF{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Fondos_{numero_limpio}.pdf"
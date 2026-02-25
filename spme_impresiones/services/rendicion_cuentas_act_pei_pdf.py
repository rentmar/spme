# services/rendicion_cuentas_act_pei_pdf.py
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import RendicionCuentasActPei
from spme_estructuracion_pei.models import ActividadPei
import json
from datetime import datetime

class RendicionCuentasActPeiPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Rendición de Cuentas de Actividad PEI
    Para rendiciones que NO tienen tarea asociada (solo actividad)
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_cuentas_act_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para RendicionCuentasActPei sin tarea
        """
        if not isinstance(obj, RendicionCuentasActPei):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentasActPei")
        
        # Validar que sea actividad (sin tarea)
        if obj.tarea:
            raise ValueError("Este generador es solo para rendiciones de actividad")
        
        # Obtener datos del usuario que rinde cuentas
        nombre_rendidor = "No asignado"
        documento_identidad = "No asignado"
        cargo = "No asignado"
        
        if obj.usuario:
            nombre_rendidor = f"{obj.usuario.nombre or ''} {obj.usuario.paterno or ''}".strip()
            documento_identidad = obj.usuario.ci or "No asignado"
            cargo = obj.usuario.cargo or "No asignado"
        
        # Procesar detalle de gastos
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        
        # Obtener datos de responsables
        nombre_responsable = "No asignado"
        if obj.responsable:
            nombre_responsable = f"{obj.responsable.nombre or ''} {obj.responsable.paterno or ''}".strip()
        
        nombre_coordinador = "No asignado"
        if obj.coordinador:
            nombre_coordinador = f"{obj.coordinador.nombre or ''} {obj.coordinador.paterno or ''}".strip()
        
        nombre_contador = "No asignado"
        if obj.contador:
            nombre_contador = f"{obj.contador.nombre or ''} {obj.contador.paterno or ''}".strip()
        
        nombre_administrador = "No asignado"
        if obj.administrador:
            nombre_administrador = f"{obj.administrador.nombre or ''} {obj.administrador.paterno or ''}".strip()
        
        # Obtener actividad
        actividad = obj.actividad
        
        # Mapeo de estados
        estados_map = dict(ActividadPei.ESTADOS_ACTIVIDAD)
        
        # Determinar tipo de solicitud asociada
        tipo_solicitud = "Ninguna"
        numero_solicitud = ""
        if obj.solicitudFondos:
            tipo_solicitud = "Fondos"
            numero_solicitud = obj.solicitudFondos.numeroFormulario or ""
        elif obj.solicitudReembolso:
            tipo_solicitud = "Reembolso"
            numero_solicitud = obj.solicitudReembolso.numeroFormulario or ""
        elif obj.solicitudViaje:
            tipo_solicitud = "Viaje"
            numero_solicitud = obj.solicitudViaje.numeroFormulario or ""
        elif obj.solicitudPagoDirecto:
            tipo_solicitud = "Pago Directo"
            numero_solicitud = obj.solicitudPagoDirecto.numeroFormulario or ""
        
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"RC-ACT-{obj.id:04d}",
            'cpte_diario': obj.cpteDiario or "No especificado",
            'fecha_emision': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else datetime.now().strftime('%d/%m/%Y'),
            'fecha_rendicion': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada",
            'fecha_desembolso': obj.fechaDesembolso.strftime('%d/%m/%Y') if obj.fechaDesembolso else "No especificada",
            
            # Información del rendidor
            'nombre_rendidor': nombre_rendidor,
            'documento_identidad': documento_identidad,
            'cargo': cargo,
            
            # Información de montos
            'monto_asignado': float(obj.montoAsignado) if obj.montoAsignado else 0,
            'monto_descargado': float(obj.montoDescargado) if obj.montoDescargado else 0,
            'saldo': float(obj.saldo) if obj.saldo else 0,
            
            # Información de la ACTIVIDAD
            'codigo_actividad': actividad.codigo if actividad else "N/A",
            'nombre_actividad': actividad.nombreCorto if actividad else "No especificado",
            'estado_actividad': estados_map.get(actividad.estado, actividad.estado) if actividad and actividad.estado else "N/A",
            
            # Datos de la actividad
            'fecha_actividad': obj.fechaActividad.strftime('%d/%m/%Y') if obj.fechaActividad else "No especificada",
            'descripcion_actividad': obj.descripcionActividad or (actividad.descripcion if actividad else "No especificada"),
            'lugar_actividad': obj.lugarActividad or "No especificado",
            'lugar_rendicion': obj.lugarRendicion or "No especificado",
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'total_gastos': total_gastos_calculado,
            'cantidad_items': len(detalle_gastos),
            'tiene_detalle': len(detalle_gastos) > 0,
            
            # Información de validaciones
            'nombre_responsable': nombre_responsable,
            'nombre_coordinador': nombre_coordinador,
            'nombre_contador': nombre_contador,
            'nombre_administrador': nombre_administrador,
            
            # Estados de validación
            'validacion_responsable': obj.validacionResponsable,
            'validacion_coordinador': obj.validacionCoordinador,
            'validacion_contador': obj.validacionContador,
            'validacion_administrador': obj.validacionAdministrador,
            
            # Información de solicitud asociada
            'tipo_solicitud': tipo_solicitud,
            'numero_solicitud': numero_solicitud,
            
            # Metadatos del documento
            'tipo_documento': 'RENDICIÓN DE CUENTAS',
            'subtipo_documento': 'Actividad PEI',
            
            # Flags
            'es_actividad': True,
            'tiene_tarea': False,
        }
        
        return context
    
    def _get_nombre_completo(self, usuario):
        """Obtiene nombre completo de cualquier usuario"""
        if not usuario:
            return "No asignado"
        
        partes = []
        if usuario.nombre:
            partes.append(usuario.nombre)
        if usuario.paterno:
            partes.append(usuario.paterno)
        if usuario.materno:
            partes.append(usuario.materno)
        
        return " ".join(partes) if partes else str(usuario)
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del JSON
        """
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleDestinoFondos:
            return detalle_gastos, total_monto
        
        try:
            data_dict = obj.detalleDestinoFondos
            
            if isinstance(data_dict, str):
                data_dict = json.loads(data_dict)
            
            items_list = []
            if isinstance(data_dict, dict) and 'items' in data_dict:
                items_list = data_dict['items']
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            for index, item in enumerate(items_list):
                if isinstance(item, dict):
                    # Formatear fecha
                    fecha_gasto = "No especificada"
                    if item.get('fecha'):
                        try:
                            fecha_obj = datetime.strptime(item['fecha'], '%Y-%m-%d')
                            fecha_gasto = fecha_obj.strftime('%d/%m/%Y')
                        except:
                            fecha_gasto = item['fecha']
                    
                    partida = item.get('partida') or item.get('partida_sf') or f"{index + 1}"
                    factura = item.get('factura_recibo') or item.get('factura') or item.get('recibo') or '-'
                    concepto = item.get('concepto') or item.get('descripcion') or f"Gasto {index + 1}"
                    
                    monto_raw = item.get('monto') or item.get('valor') or item.get('importe') or 0
                    try:
                        monto = float(monto_raw)
                        total_monto += monto
                    except (ValueError, TypeError):
                        monto = 0.0
                    
                    detalle_gastos.append({
                        'indice': index + 1,
                        'fecha': fecha_gasto,
                        'partida': str(partida),
                        'factura': str(factura),
                        'concepto': str(concepto),
                        'monto': monto,
                    })
        
        except Exception as e:
            print(f"Error procesando detalle de gastos: {e}")
        
        return detalle_gastos, total_monto
    
    def generate_filename(self, obj):
        """Genera el nombre del archivo PDF"""
        numero = obj.numeroFormulario or f"RC-ACT-{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Rendicion_Cuentas_Actividad_PEI_{numero_limpio}.pdf"
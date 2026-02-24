# services/solicitud_viaje_act_pei_pdf.py
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudViajeActPei
import json

class SolicitudViajeActPeiPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Viaje de Actividad PEI
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_viaje_act_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para SolicitudViajeActPei
        """
        if not isinstance(obj, SolicitudViajeActPei):
            raise ValueError("El objeto debe ser una instancia de SolicitudViajeActPei")
        
        # Validar que sea actividad (sin tarea)
        if obj.tarea:
            raise ValueError("Este generador es solo para solicitudes de actividad")
        
        # Procesar detalle de gastos
        detalle_gastos, total_gastos_calculado = self._procesar_detalle_gastos(obj)
        
        # Usar monto solicitado del objeto o calcularlo
        monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else total_gastos_calculado
        
        context = {
            # Información del formulario
            'numero_formulario': obj.numeroFormulario or f"SV-ACT-{obj.id:04d}",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            
            # Información del solicitante
            'nombre_solicitante': self._get_nombre_completo_solicitante(obj),
            'documento_identidad': self._get_documento_identidad(obj),
            'cargo': self._get_cargo(obj),
            
            # Información de la actividad
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'estado_actividad': self._get_estado_actividad(obj),
            
            # Información específica del viaje
            'evento': obj.evento or "No especificado",
            'lugar_evento': obj.lugarEvento or "No especificado",
            'fecha_evento': obj.fechaEvento.strftime('%d/%m/%Y') if obj.fechaEvento else "No especificada",
            'instituciones_participantes': obj.institucionesParticipantes or "No especificado",
            'organizador': obj.organizador or "No especificado",
            'quien_cubre_gastos': obj.quienCubreGastos or "No especificado",
            'justificacion_asistencia': obj.justificacionAsistencia or "No especificada",
            'fondos_unitas': obj.fondosUnitas or "No especificado",
            'tareas_previas': obj.tareasPrevias or "No especificado",
            
            # Información del lugar y pago
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'total_monto_solicitado': monto_solicitado,
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            
            # Información de validaciones
            'nombre_responsable': self._get_nombre_completo(obj.responsable),
            'nombre_coordinador': self._get_nombre_completo(obj.coordinador),
            
            # Información bancaria del solicitante
            'datos_bancarios_solicitante': self._get_datos_bancarios_solicitante(obj),
            
            # Metadatos del documento
            'tipo_documento': 'SOLICITUD DE VIAJE',
            'subtipo_documento': 'Actividad PEI',
        }
        
        # Procesar datos de transferencia específicos del formulario
        context['datos_transferencia'] = self._procesar_datos_transferencia(obj)
        
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
        
        return "No asignado"
    
    def _get_nombre_completo(self, usuario):
        """Obtiene nombre completo de cualquier usuario"""
        if not usuario:
            return "No asignado"
        
        if hasattr(usuario, 'get_full_name'):
            nombre = usuario.get_full_name()
            if nombre and nombre.strip():
                return nombre
        
        partes = []
        if usuario.nombre:
            partes.append(usuario.nombre)
        if usuario.paterno:
            partes.append(usuario.paterno)
        if usuario.materno:
            partes.append(usuario.materno)
        
        return " ".join(partes) if partes else str(usuario)
    
    def _get_documento_identidad(self, obj):
        """Obtiene el documento de identidad"""
        return obj.usuario.ci if obj.usuario else "No asignado"
    
    def _get_cargo(self, obj):
        """Obtiene el cargo del solicitante"""
        return obj.usuario.cargo if obj.usuario else "No asignado"
    
    def _get_estado_actividad(self, obj):
        """Obtiene el estado de la actividad formateado"""
        if obj.actividad and obj.actividad.estado:
            estado = obj.actividad.estado
            estados_map = {
                'CRD': 'Creada',
                'PLAN': 'Planificada',
                'RETR': 'Retraso',
                'REPROG': 'Reprogramación',
                'EJEC': 'En Ejecución',
                'REP': 'En Reporte',
                'FIN': 'Finalizado',
            }
            return estados_map.get(estado, estado)
        return "No especificado"
    
    def _get_datos_bancarios_solicitante(self, obj):
        """Obtiene los datos bancarios del solicitante"""
        datos = {}
        if obj.usuario:
            datos = {
                'banco': obj.usuario.banco or '',
                'numero_cuenta': obj.usuario.numero_cuenta or '',
                'tipo_cuenta': obj.usuario.tipo_cuenta or '',
                'nombre_completo': self._get_nombre_completo_solicitante(obj),
                'ci': obj.usuario.ci or '',
            }
        return datos
    
    def _procesar_detalle_gastos(self, obj):
        """
        Procesa el detalle de gastos del JSON.
        Formato esperado: Lista de objetos con descripción, monto, etc.
        """
        detalle_gastos = []
        total_monto = 0.0
        
        if not obj.detalleGasto:
            return detalle_gastos, total_monto
        
        try:
            data_dict = obj.detalleGasto
            
            if isinstance(data_dict, str):
                try:
                    data_dict = json.loads(data_dict)
                except json.JSONDecodeError:
                    return detalle_gastos, total_monto
            
            items_list = []
            
            if isinstance(data_dict, dict):
                if 'items' in data_dict:
                    items_list = data_dict['items']
                elif 'gastos' in data_dict:
                    items_list = data_dict['gastos']
                else:
                    # Si es un diccionario con una sola entrada, tratarlo como un item
                    items_list = [data_dict]
            elif isinstance(data_dict, list):
                items_list = data_dict
            
            if not isinstance(items_list, list):
                return detalle_gastos, total_monto
            
            for index, item in enumerate(items_list):
                if not isinstance(item, dict):
                    continue
                
                # Extraer campos específicos para viaje
                concepto = (
                    item.get('concepto') or 
                    item.get('descripcion') or 
                    item.get('gasto') or 
                    f"Gasto {index + 1}"
                )
                
                # Tipo de gasto (pasaje, hospedaje, viáticos, etc.)
                tipo_gasto = (
                    item.get('tipo') or 
                    item.get('categoria') or 
                    item.get('rubro') or 
                    'General'
                )
                
                monto_raw = (
                    item.get('monto') or 
                    item.get('valor') or 
                    item.get('importe') or 
                    item.get('costo') or 
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
                    '-'
                )
                
                detalle_gastos.append({
                    'indice': index + 1,
                    'tipo_gasto': str(tipo_gasto),
                    'concepto': str(concepto),
                    'monto': monto,
                    'observaciones': str(observaciones),
                })
            
        except Exception as e:
            print(f"Error en _procesar_detalle_gastos: {e}")
        
        return detalle_gastos, total_monto
    
    def _procesar_datos_transferencia(self, obj):
        """Procesa los datos de forma de pago del formulario"""
        datos_forma_pago = {
            'tipo': 'otros',
            'otros': {},
            'transferencia': {},
            'mostrar_transferencia': False,
            'mostrar_otros': False,
        }
        
        if not obj.datos_forma_pago:
            return datos_forma_pago
        
        try:
            if isinstance(obj.datos_forma_pago, dict):
                datos_forma_pago.update(obj.datos_forma_pago)
                
                tiene_datos_otros = datos_forma_pago.get('otros', {}).get('nombre_otros')
                tiene_datos_transferencia = datos_forma_pago.get('transferencia', {}).get('nombre_transferencia')
                
                if obj.formaPago and 'transferencia' in obj.formaPago.formaPago.lower():
                    datos_forma_pago['tipo'] = 'transferencia'
                    datos_forma_pago['mostrar_transferencia'] = True
                    datos_forma_pago['mostrar_otros'] = False
                elif tiene_datos_otros:
                    datos_forma_pago['tipo'] = 'otros'
                    datos_forma_pago['mostrar_transferencia'] = False
                    datos_forma_pago['mostrar_otros'] = True
                else:
                    if tiene_datos_transferencia:
                        datos_forma_pago['tipo'] = 'transferencia'
                        datos_forma_pago['mostrar_transferencia'] = True
                    elif tiene_datos_otros:
                        datos_forma_pago['tipo'] = 'otros'
                        datos_forma_pago['mostrar_otros'] = True
            
            elif isinstance(obj.datos_forma_pago, str):
                try:
                    parsed_data = json.loads(obj.datos_forma_pago)
                    datos_forma_pago.update(parsed_data)
                except json.JSONDecodeError:
                    pass
        
        except Exception as e:
            print(f"Error procesando datos de forma de pago: {e}")
        
        return datos_forma_pago
    
    def generate_filename(self, obj):
        """Genera el nombre del archivo PDF"""
        numero = obj.numeroFormulario or f"SV-ACT-{obj.id:04d}"
        numero_limpio = "".join(c for c in numero if c.isalnum() or c in ['-', '_'])
        return f"Solicitud_Viaje_Actividad_PEI_{numero_limpio}.pdf"
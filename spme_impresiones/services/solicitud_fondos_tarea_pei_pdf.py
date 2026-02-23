# services/solicitud_fondos_tarea_pei_pdf.py
import json
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudFondosActPei
from spme_estructuracion_pei.models import TareaActividadPei, ActividadPei
from django.utils import timezone

class SolicitudFondosTareaPeiPDFGenerator(BasePDFGenerator):
    """
    Generador ESPECÍFICO para Solicitud de Fondos de Tarea PEI
    Basado en SolicitudFondosTareaPDFGenerator
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_fondos_tarea_pei_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto ESPECÍFICO para Solicitud de Fondos de Tarea PEI
        """
        if not isinstance(obj, SolicitudFondosActPei):
            raise ValueError("El objeto debe ser una instancia de SolicitudFondosActPei")
        
        # NOTA: El ViewSet ya validó que tiene tarea, pero manejamos el caso por si acaso
        if not obj.tarea:
            # En lugar de lanzar error, devolvemos un contexto con mensaje
            return {
                'tipo_documento': 'SOLICITUD DE FONDOS - ERROR',
                'subtipo_documento': 'Sin tarea asociada',
                'numero_formulario': obj.numeroFormulario or f"SF-{obj.id:04d}",
                'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else timezone.now().strftime('%d/%m/%Y'),
                'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else timezone.now().strftime('%d/%m/%Y'),
                'nombre_solicitante': self._get_nombre_completo(obj.usuario),
                'documento_identidad': obj.usuario.ci if obj.usuario else "N/A",
                'cargo_solicitante': obj.usuario.cargo if obj.usuario else "N/A",
                'mensaje_error': 'Esta solicitud no tiene una tarea asociada. Use el endpoint de actividades.',
                'detalle_gastos': [],
                'total_monto_solicitado': 0,
                'tiene_error': True,
            }
        
        tarea = obj.tarea
        actividad = obj.actividad
        
        # ===== INFORMACIÓN DE LA TAREA PEI =====
        codigo_tarea = tarea.codigo if tarea.codigo else "No asignado"
        titulo_tarea = tarea.titulo if tarea.titulo else "Sin título"
        descripcion_tarea = tarea.descripcion if tarea.descripcion else "Sin descripción"
        
        # Estado con display
        estado_tarea_raw = tarea.estado if tarea.estado else 'PEN'
        estados_dict = dict(TareaActividadPei.ESTADOS_TAREA)
        estado_tarea_display = estados_dict.get(estado_tarea_raw, estado_tarea_raw)
        
        # Fechas
        fecha_ejecucion_tarea = tarea.fecha_ejecucion.strftime('%d/%m/%Y') if tarea.fecha_ejecucion else "No especificada"
        fecha_creacion_tarea = tarea.fecha_creacion.strftime('%d/%m/%Y') if tarea.fecha_creacion else "No especificada"
        fecha_limite_tarea = tarea.fecha_limite.strftime('%d/%m/%Y') if tarea.fecha_limite else "No especificada"
        
        # Presupuesto
        presupuesto_tarea = float(tarea.presupuesto) if tarea.presupuesto else 0.00
        
        # ===== INFORMACIÓN DE LA ACTIVIDAD PEI =====
        actividad = tarea.actividad if tarea else None
        codigo_actividad = actividad.codigo if actividad else "N/A"
        nombre_actividad = actividad.nombreCorto if actividad else "N/A"
        estado_actividad = actividad.estado if actividad else "N/A"
        
        # ===== INFORMACIÓN DEL SOLICITANTE =====
        usuario = obj.usuario
        nombre_completo_solicitante = ""
        documento_identidad = ""
        cargo_solicitante = ""
        
        if usuario:
            partes = []
            if hasattr(usuario, 'nombre') and usuario.nombre:
                partes.append(usuario.nombre)
            if hasattr(usuario, 'paterno') and usuario.paterno:
                partes.append(usuario.paterno)
            if hasattr(usuario, 'materno') and usuario.materno:
                partes.append(usuario.materno)
            nombre_completo_solicitante = " ".join(partes) if partes else str(usuario)
            
            documento_identidad = usuario.ci if hasattr(usuario, 'ci') and usuario.ci else "N/A"
            cargo_solicitante = usuario.cargo if hasattr(usuario, 'cargo') and usuario.cargo else "No especificado"
        
        # ===== INFORMACIÓN DE LA SOLICITUD =====
        total_monto_solicitado = float(obj.montoSolicitado) if obj.montoSolicitado else 0.00
        fecha_solicitud = obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else timezone.now().strftime('%d/%m/%Y')
        
        if obj.fechaRealizacionActividad:
            fecha_realizacion = obj.fechaRealizacionActividad.strftime('%d/%m/%Y')
        elif tarea and tarea.fecha_ejecucion:
            fecha_realizacion = tarea.fecha_ejecucion.strftime('%d/%m/%Y')
        else:
            fecha_realizacion = "No especificada"
        
        # ===== DETALLE DE GASTOS =====
        detalle_gastos = []
        total_gastos_calculado = 0
        
        if obj.detalleDestinoFondos:
            try:
                if isinstance(obj.detalleDestinoFondos, str):
                    datos_gastos = json.loads(obj.detalleDestinoFondos)
                else:
                    datos_gastos = obj.detalleDestinoFondos
                
                if isinstance(datos_gastos, dict) and 'items' in datos_gastos:
                    items = datos_gastos['items']
                    if isinstance(items, list):
                        for idx, item in enumerate(items, 1):
                            if isinstance(item, dict):
                                monto = float(item.get('monto', 0))
                                total_gastos_calculado += monto
                                
                                detalle_gastos.append({
                                    'numero': idx,
                                    'partida': item.get('partida_sf', item.get('partida', f'Partida {idx}')),
                                    'descripcion_gasto': item.get('concepto', item.get('descripcion', 'Sin descripción')),
                                    'monto': monto,
                                    'observaciones': item.get('observaciones', '')
                                })
                
                elif isinstance(datos_gastos, list):
                    for idx, item in enumerate(datos_gastos, 1):
                        if isinstance(item, dict):
                            monto = float(item.get('monto', item.get('Monto', 0)))
                            total_gastos_calculado += monto
                            
                            detalle_gastos.append({
                                'numero': idx,
                                'partida': item.get('partida', item.get('partida_sf', item.get('Partida', f'Partida {idx}'))),
                                'descripcion_gasto': item.get('descripcionGasto', item.get('concepto', item.get('descripcion', 'Sin descripción'))),
                                'monto': monto,
                                'observaciones': item.get('observaciones', item.get('Observaciones', ''))
                            })
                            
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Error procesando detalleDestinoFondos: {e}")
                detalle_gastos.append({
                    'numero': 1,
                    'partida': 'Error',
                    'descripcion_gasto': f'Error procesando datos: {str(e)}',
                    'monto': 0,
                    'observaciones': 'Formato inválido'
                })
        
        monto_final = total_gastos_calculado if total_gastos_calculado > 0 else total_monto_solicitado
        
        # ===== DETECCIÓN DE TIPO DE PAGO =====
        forma_pago_obj = obj.formaPago
        forma_pago_codigo = forma_pago_obj.codigo if forma_pago_obj else ""
        forma_pago_nombre = forma_pago_obj.formaPago if forma_pago_obj else "No especificada"
        
        # Inicializar variables
        datos_transferencia = {}
        datos_efectivo = {}
        datos_cheque = {}
        tipo_pago = "desconocido"
        
        # Determinar tipo de pago basado en el código
        if forma_pago_codigo == "TB":
            tipo_pago = "transferencia"
        elif forma_pago_codigo == "EFEC":
            tipo_pago = "efectivo"
        elif forma_pago_codigo == "CHE":
            tipo_pago = "cheque"
        else:
            # Si no hay código, intentar deducir del nombre
            forma_pago_lower = forma_pago_nombre.lower()
            if "transferencia" in forma_pago_lower:
                tipo_pago = "transferencia"
            elif "efectivo" in forma_pago_lower:
                tipo_pago = "efectivo"
            elif "cheque" in forma_pago_lower:
                tipo_pago = "cheque"
        
        # ===== PROCESAR DATOS DE PAGO =====
        if obj.datos_forma_pago:
            try:
                if isinstance(obj.datos_forma_pago, str):
                    datos_pago = json.loads(obj.datos_forma_pago)
                else:
                    datos_pago = obj.datos_forma_pago
                
                if isinstance(datos_pago, dict):
                    # Datos de transferencia (si existen)
                    if 'transferencia' in datos_pago and datos_pago['transferencia']:
                        transferencia = datos_pago['transferencia']
                        datos_transferencia = {
                            'nombre': transferencia.get('nombre_transferencia', ''),
                            'ci': transferencia.get('ci_transferencia', ''),
                            'entidad_bancaria': transferencia.get('entidad_bancaria', ''),
                            'tipo_cuenta': transferencia.get('tipo_cuenta', ''),
                            'numero_cuenta': transferencia.get('numero_cuenta', ''),
                            'tiene_datos': any([
                                transferencia.get('nombre_transferencia'),
                                transferencia.get('ci_transferencia'),
                                transferencia.get('entidad_bancaria'),
                                transferencia.get('numero_cuenta')
                            ])
                        }
                    
                    # Datos de efectivo/otros (para EFEC y CHE)
                    if 'otros' in datos_pago and datos_pago['otros']:
                        otros = datos_pago['otros']
                        datos_efectivo = {
                            'nombre': otros.get('nombre_otros', ''),
                            'ci': otros.get('ci_otros', ''),
                            'tiene_datos': any([otros.get('nombre_otros'), otros.get('ci_otros')])
                        }
                        # Los mismos datos sirven para cheque
                        datos_cheque = datos_efectivo.copy()
                        
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error procesando datos_forma_pago: {e}")
        
        # ===== INFORMACIÓN DE VALIDACIONES =====
        nombre_contador = ""
        nombre_coordinador = ""
        
        if obj.contador:
            partes = []
            if hasattr(obj.contador, 'nombre') and obj.contador.nombre:
                partes.append(obj.contador.nombre)
            if hasattr(obj.contador, 'paterno') and obj.contador.paterno:
                partes.append(obj.contador.paterno)
            if hasattr(obj.contador, 'materno') and obj.contador.materno:
                partes.append(obj.contador.materno)
            nombre_contador = " ".join(partes) if partes else str(obj.contador)
        
        if obj.coordinador:
            partes = []
            if hasattr(obj.coordinador, 'nombre') and obj.coordinador.nombre:
                partes.append(obj.coordinador.nombre)
            if hasattr(obj.coordinador, 'paterno') and obj.coordinador.paterno:
                partes.append(obj.coordinador.paterno)
            if hasattr(obj.coordinador, 'materno') and obj.coordinador.materno:
                partes.append(obj.coordinador.materno)
            nombre_coordinador = " ".join(partes) if partes else str(obj.coordinador)
        
        # ===== CÁLCULOS =====
        diferencia_presupuesto = presupuesto_tarea - monto_final
        dentro_presupuesto = diferencia_presupuesto >= 0
        porcentaje_uso = (monto_final / presupuesto_tarea * 100) if presupuesto_tarea > 0 else 0
        
        # ===== CONTEXTO COMPLETO =====
        context = {
            # Documento
            'tipo_documento': 'SOLICITUD DE FONDOS - TAREA PEI',
            'subtipo_documento': 'F-T-PEI',
            'numero_formulario': obj.numeroFormulario or f"SF-T-PEI-{obj.id:04d}",
            'fecha_emision': fecha_solicitud,
            'fecha_solicitud': fecha_solicitud,
            
            # Tarea PEI
            'codigo_tarea': codigo_tarea,
            'titulo_tarea': titulo_tarea,
            'descripcion_tarea': descripcion_tarea,
            'estado_tarea': estado_tarea_display,
            'estado_tarea_raw': estado_tarea_raw,
            'fecha_ejecucion_tarea': fecha_ejecucion_tarea,
            'fecha_creacion_tarea': fecha_creacion_tarea,
            'fecha_limite_tarea': fecha_limite_tarea,
            'presupuesto_tarea': presupuesto_tarea,
            
            # Actividad PEI
            'codigo_actividad': codigo_actividad,
            'nombre_actividad': nombre_actividad,
            'estado_actividad': estado_actividad,
            'tiene_actividad_asociada': bool(actividad),
            
            # Solicitante
            'nombre_solicitante': nombre_completo_solicitante,
            'documento_identidad': documento_identidad,
            'cargo_solicitante': cargo_solicitante,
            
            # Solicitud
            'fecha_realizacion': fecha_realizacion,
            'fecha_ejecucion': fecha_realizacion,  # Alias para compatibilidad
            'descripcion_actividad': obj.descripcion_actividad or descripcion_tarea,
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'forma_pago': forma_pago_nombre,
            'forma_pago_codigo': forma_pago_codigo,
            'total_monto_solicitado': monto_final,
            
            # Tipo de pago detectado
            'tipo_pago': tipo_pago,
            'es_transferencia': tipo_pago == "transferencia",
            'es_efectivo': tipo_pago == "efectivo",
            'es_cheque': tipo_pago == "cheque",
            
            # Datos de pago (según tipo)
            'datos_transferencia': datos_transferencia,
            'datos_efectivo': datos_efectivo,
            'datos_cheque': datos_cheque,
            'tiene_datos_transferencia': datos_transferencia.get('tiene_datos', False),
            'tiene_datos_efectivo': datos_efectivo.get('tiene_datos', False),
            'tiene_datos_cheque': datos_cheque.get('tiene_datos', False),
            
            # Validaciones
            'validacion_responsable': "✓ APROBADO" if obj.validacionResponsable else "⏰ PENDIENTE",
            'validacion_coordinador': "✓ APROBADO" if obj.validacionCoordinador else "⏰ PENDIENTE",
            'nombre_contador': nombre_contador or "No asignado",
            'nombre_coordinador': nombre_coordinador or "No asignado",
            
            # Detalle de gastos
            'detalle_gastos': detalle_gastos,
            'tiene_detalle_gastos': len(detalle_gastos) > 0,
            
            # Estado de validaciones
            'esta_validado_responsable': obj.validacionResponsable,
            'esta_validado_coordinador': obj.validacionCoordinador,
            
            # Cálculos
            'diferencia_presupuesto': diferencia_presupuesto,
            'dentro_presupuesto': dentro_presupuesto,
            'porcentaje_uso': porcentaje_uso,
            
            # Bloquear iconos
            'bloquear_iconos': obj.bloquearIconosSolFondos,
            
            # Flag de error (si no tiene tarea)
            'tiene_error': False,
        }
        
        return context
    
    def _get_nombre_completo(self, usuario):
        """Obtiene nombre completo del usuario"""
        if not usuario:
            return "No asignado"
        
        partes = []
        if hasattr(usuario, 'nombre') and usuario.nombre:
            partes.append(usuario.nombre)
        if hasattr(usuario, 'paterno') and usuario.paterno:
            partes.append(usuario.paterno)
        if hasattr(usuario, 'materno') and usuario.materno:
            partes.append(usuario.materno)
        
        return " ".join(partes) if partes else str(usuario)
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        if self.filename:
            return self.filename
            
        if obj.tarea and obj.tarea.codigo:
            codigo_limpio = obj.tarea.codigo.replace('/', '-')
            return f"Solicitud_Fondos_Tarea_PEI_{codigo_limpio}.pdf"
        elif obj.numeroFormulario:
            numero_limpio = obj.numeroFormulario.replace('/', '-')
            return f"Solicitud_Fondos_Tarea_PEI_{numero_limpio}.pdf"
        else:
            return f"Solicitud_Fondos_Tarea_PEI_ID{obj.id}.pdf"
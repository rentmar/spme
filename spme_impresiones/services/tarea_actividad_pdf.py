#spme_impresiones/services/tarea_actividad_pdf.py

from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import TareaActividad 
import json
from datetime import datetime, date

class TareaActividadPDFGenerator(BasePDFGenerator):
    """
    Generador específico para TareaActividad 
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/tarea_actividad_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para TareaActividad
        """
        if not isinstance(obj, TareaActividad):
            raise ValueError("El objeto debe ser una instancia de TareaActividad")
        
        # Mapeo de estados
        estados_map = {
            'PEN': 'Pendiente',
            'EPROG': 'En Progreso',
            'COMPL': 'Completada'
        }
        
        # Obtener información de la actividad asociada
        actividad_info = {}
        if obj.actividad:
            actividad_info = {
                'codigo': obj.actividad.codigo if hasattr(obj.actividad, 'codigo') else 'N/A',
                'nombre': obj.actividad.nombreCorto if hasattr(obj.actividad, 'nombreCorto') else str(obj.actividad),
                'descripcion': obj.actividad.descripcion if hasattr(obj.actividad, 'descripcion') else '',
            }
        
        # Procesar presupuesto desglose
        presupuesto_items = []
        presupuesto_total_calculado = 0.0
        
        if obj.presupuestoDesglose:
            try:
                items = obj.presupuestoDesglose
                if isinstance(items, str):
                    items = json.loads(items)
                
                if isinstance(items, list):
                    for idx, item in enumerate(items):
                        if isinstance(item, dict):
                            monto = float(item.get('monto', 0))
                            presupuesto_total_calculado += monto
                            presupuesto_items.append({
                                'indice': idx + 1,
                                'partida': item.get('partida', '-'),
                                'descripcion': item.get('descripcion', '-'),
                                'monto': monto,
                            })
            except Exception as e:
                print(f"Error procesando presupuestoDesglose: {e}")
        
        # Calcular días restantes o retraso
        dias_restantes = None
        dias_retraso = None
        estado_plazo = 'sin_plazo'
        
        if obj.fecha_limite:
            hoy = date.today()
            if obj.fecha_limite >= hoy:
                dias_restantes = (obj.fecha_limite - hoy).days
                estado_plazo = 'normal'
            else:
                dias_retraso = (hoy - obj.fecha_limite).days
                estado_plazo = 'vencido'
        
        # Determinar porcentaje de progreso según estado
        progreso = {
            'PEN': 10,
            'EPROG': 50,
            'COMPL': 100
        }.get(obj.estado, 0)
        
        context = {
            # Información básica de la tarea
            'numero_formulario': obj.codigo or f"TAREA-{obj.id:04d}",
            'codigo_tarea': obj.codigo or f"TAREA-{obj.id:04d}",
            'titulo_tarea': obj.titulo or "Sin título",
            'descripcion_tarea': obj.descripcion or "Sin descripción",
            'estado_tarea': estados_map.get(obj.estado, obj.estado),
            'estado_codigo': obj.estado,
            'progreso_porcentaje': progreso,
            
            # Fechas importantes
            'fecha_creacion': obj.fecha_creacion.strftime('%d/%m/%Y') if obj.fecha_creacion else "No especificada",
            'fecha_creacion_obj': obj.fecha_creacion,
            'fecha_ejecucion': obj.fecha_ejecucion.strftime('%d/%m/%Y') if obj.fecha_ejecucion else "No programada",
            'fecha_limite': obj.fecha_limite.strftime('%d/%m/%Y') if obj.fecha_limite else "Sin fecha límite",
            'fecha_limite_obj': obj.fecha_limite,
            
            # Presupuesto
            'presupuesto_total': float(obj.presupuesto) if obj.presupuesto else 0.00,
            'presupuesto_calculado': presupuesto_total_calculado,
            'presupuesto_items': presupuesto_items,
            'cantidad_partidas': len(presupuesto_items),
            'presupuesto_coincide': abs(presupuesto_total_calculado - (float(obj.presupuesto) if obj.presupuesto else 0)) < 0.01,
            
            # Actividad asociada
            'actividad_asociada': actividad_info,
            'tiene_actividad': bool(obj.actividad),
            
            # Plazos
            'dias_restantes': dias_restantes,
            'dias_retraso': dias_retraso,
            'estado_plazo': estado_plazo,
            
            # Metadatos del documento
            'tipo_documento': 'IMPRESION SUBACTIVIDAD',
            'subtipo_documento': 'SUBACTIVIDAD',
        }
        
        return context
    
    def generate_filename(self, obj):
        """Genera el nombre del archivo PDF"""
        if obj.codigo:
            nombre_base = obj.codigo.replace('/', '-').replace('\\', '-')
        else:
            nombre_base = f"subactividad_{obj.id:04d}"
        
        return f"subactividad_{nombre_base}.pdf"
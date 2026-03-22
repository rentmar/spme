"""
Generador de PDF para Informe de Tarea Principal.
Utiliza el modelo ValidacionInformeTarea para obtener:
- Redactor (usuarioRedactor de la validación)
- Validadores (múltiples, desde las validaciones asociadas)
- Estados de validación
"""

from .pdf_base import BasePDFGenerator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InformeTareaPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Informe de Tarea Principal
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/informe_tarea_template.html'
        self.sufijo = 'TAREA'
    
    # Sobrescribir generate_filename para usar numeroInforme
    def generate_filename(self, obj):
        """
        Sobrescribe el método de la clase base para usar numeroInforme
        """
        tipo = self.__class__.__name__.replace('PDFGenerator', '')
        numero = obj.numeroInforme or f"{obj.id:04d}"
        sufijo = f"_{self.sufijo}" if self.sufijo else ""
        return f"{tipo}{sufijo}_{numero}.pdf"
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Informe de Tarea
        """
        # Importar directamente desde models
        from spme_validaciones.models import ValidacionInformeTarea
        
        if not self._es_instancia_valida(obj):
            raise ValueError("El objeto debe ser una instancia de InformeTareaPrincipal")
        
        # Obtener todas las validaciones asociadas a este informe
        validaciones = list(
            ValidacionInformeTarea.objects.filter(
                informeTarea=obj
            ).select_related(
                'usuarioValidador',
                'usuarioRedactor'
            ).order_by('fechaAsignacion')
        )
        
        logger.info(f"Se encontraron {len(validaciones)} validaciones para el informe de tarea {obj.id}")
        
        # Obtener redactor (es el mismo para todas las validaciones)
        redactor = None
        if validaciones:
            redactor = validaciones[0].usuarioRedactor
            logger.info(f"Redactor encontrado: {redactor}")
        
        # Información de la tarea
        tarea = obj.tarea
        actividad = tarea.actividad if tarea else None
        
        # Responsable viene de la actividad, no de la tarea
        responsable = None
        if actividad and actividad.responsable:
            responsable = actividad.responsable
        elif obj.usuario:
            responsable = obj.usuario  # Fallback al usuario que creó el informe
        
        # Información básica del informe
        context = {
            # Identificación del documento
            'numero_informe': self._obtener_numero_informe(obj),
            'fecha_ejecucion': self._formatear_fecha(obj.fechaEjecucion),
            'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'tipo_documento': 'INFORME DE TAREA',
            'subtipo_documento': 'F-IT-01',
            'sufijo_documento': self.sufijo,
            
            # Información de la tarea
            'codigo_tarea': tarea.codigo if tarea else 'No asignado',
            'nombre_tarea': tarea.titulo if tarea else 'No especificado',
            'descripcion_tarea': tarea.descripcion if tarea else 'No especificada',
            'estado_tarea': self._get_estado_tarea_display(tarea.estado) if tarea else 'No especificado',
            'fecha_inicio_tarea': self._formatear_fecha(tarea.fecha_creacion) if tarea and tarea.fecha_creacion else 'No especificada',
            'fecha_fin_tarea': self._formatear_fecha(tarea.fecha_limite) if tarea and tarea.fecha_limite else 'No especificada',
            
            # Información de la actividad padre
            'codigo_actividad': actividad.codigo if actividad else 'No asignado',
            'nombre_actividad': actividad.nombreCorto if actividad else 'No especificado',
            
            # Responsable de la tarea (desde la actividad)
            'responsable_nombre': self._obtener_nombre_completo(responsable) if responsable else 'No asignado',
            'responsable_cargo': responsable.cargo if responsable else 'No especificado',
            'responsable_ci': responsable.ci if responsable else 'No especificado',
            
            # Objetivos específicos de tarea
            'objetivo_tarea': self._obtener_objetivo_tarea(obj),
            'informe_objetivo_tarea': self._obtener_informe_objetivo_tarea(obj),
            'tipo_actividad_tarea': obj.tipoActividad or 'No especificado',
            
            # REDACTOR - Desde las validaciones
            'redactor_nombre': self._obtener_nombre_completo(redactor) if redactor else 'No especificado',
            'redactor_cargo': redactor.cargo if redactor else 'No especificado',
            'redactor_ci': redactor.ci if redactor else 'No especificado',
            'redactor_fecha': self._formatear_fecha_hora(obj.timestamp_registro),
            
            # VALIDADORES - Desde todas las validaciones
            'validadores': self._procesar_validadores(validaciones),
            
            # Resumen de validaciones
            'total_validaciones': len(validaciones),
            'validaciones_pendientes': sum(1 for v in validaciones if v.estado == 'PENDIENTE'),
            'validaciones_aprobadas': sum(1 for v in validaciones if v.estado == 'APROBADO'),
            'validaciones_rechazadas': sum(1 for v in validaciones if v.estado == 'RECHAZADO'),
            
            # Presupuesto
            'presupuesto_planificado': self._formatear_monto(obj.presupuestoPlanificado),
            'presupuesto_ejecutado': self._formatear_monto(obj.presupuestoEjecutado),
            'porcentaje_ejecucion': self._calcular_porcentaje_ejecucion(obj),
            
            # Metadatos
            'fecha_registro': self._formatear_fecha_hora(obj.timestamp_registro),
            'ultima_modificacion': self._formatear_fecha_hora(obj.timestamp_ultima_modificacion),
            'comentarios_recomendaciones': self._obtener_comentarios(obj),
        }
        
        # Procesar campos JSON con manejo de null (solo los que existen en InformeActividadBase)
        context['contribucion_proyecto'] = self._procesar_contribucion_proyecto(obj.contribucionProyecto)
        context['avance_indicadores'] = self._procesar_avance_indicadores(obj.avanceIndicadores)
        
        # Procesar información cuantitativa con manejo de null
        context['informacion_cuantitativa'] = self._procesar_informacion_cuantitativa(obj.informacionCuantitativa)
        
        context['herramientas_evaluacion'] = self._procesar_herramientas_evaluacion(obj.herramientasEvaluacion)
        
        # Procesar desglose de presupuesto (específico de tarea)
        context['desglose_presupuesto'], context['totales_desglose'] = self._procesar_desglose_presupuesto(obj.desglosePresupuesto)
        
        # Procesar medios de verificación (existe en la clase base)
        context['medios_verificacion'] = obj.mediosVerificacion or ''
        
        # Los siguientes campos NO existen en InformeTareaPrincipal
        context['archivos_cuantitativos'] = []
        context['herramientas_archivos'] = []
        context['medios_archivos'] = []
        
        # Extraer validaciones de info cuantitativa para controlar visibilidad de subsecciones
        info_cuantitativa = context['informacion_cuantitativa']
        validaciones_cuant = info_cuantitativa.get('validaciones', {}) if info_cuantitativa else {}
        
        # Crear banderas individuales para cada subsección basadas en validaciones
        context['mostrar_seccion_cuantitativa'] = bool(info_cuantitativa)
        context['mostrar_subseccion_genero'] = validaciones_cuant.get('genero', False) and info_cuantitativa.get('genero')
        context['mostrar_subseccion_edades'] = validaciones_cuant.get('edades', False) and info_cuantitativa.get('edades')
        context['mostrar_subseccion_discapacidad'] = validaciones_cuant.get('discapacidad', False) and info_cuantitativa.get('discapacidad')
        context['mostrar_subseccion_ocupaciones'] = validaciones_cuant.get('ocupaciones', False) and info_cuantitativa.get('ocupaciones')
        context['mostrar_subseccion_localidades'] = validaciones_cuant.get('localidades', False) and info_cuantitativa.get('localidades')
        context['mostrar_subseccion_organizaciones'] = validaciones_cuant.get('organizaciones', False) and info_cuantitativa.get('organizaciones')
        
        # También crear versiones de los datos para mostrar tablas completas
        if context['mostrar_subseccion_discapacidad'] and info_cuantitativa.get('discapacidad'):
            context['discapacidad_tipos'] = info_cuantitativa.get('discapacidad', {}).get('tipos', [])
            context['discapacidad_total'] = info_cuantitativa.get('discapacidad', {}).get('total', 0)
            context['discapacidad_necesidades'] = info_cuantitativa.get('discapacidad', {}).get('necesidades', '')
        
        if context['mostrar_subseccion_ocupaciones'] and info_cuantitativa.get('ocupaciones'):
            context['ocupaciones_datos'] = info_cuantitativa.get('ocupaciones', {}).get('datos', [])
            context['ocupaciones_suma'] = info_cuantitativa.get('ocupaciones', {}).get('suma', 0)
        
        if context['mostrar_subseccion_localidades'] and info_cuantitativa.get('localidades'):
            context['localidades_datos'] = info_cuantitativa.get('localidades', {}).get('datos', [])
            context['localidades_suma'] = info_cuantitativa.get('localidades', {}).get('suma', 0)
        
        if context['mostrar_subseccion_organizaciones'] and info_cuantitativa.get('organizaciones'):
            context['organizaciones_datos'] = info_cuantitativa.get('organizaciones', {}).get('datos', [])
            context['organizaciones_suma'] = info_cuantitativa.get('organizaciones', {}).get('suma', 0)
        
        # Indicadores de visualización para otras secciones
        context['mostrar_seccion_contribucion'] = bool(context['contribucion_proyecto'])
        context['mostrar_seccion_indicadores'] = bool(context['avance_indicadores'])
        context['mostrar_seccion_herramientas'] = bool(context['herramientas_evaluacion'])
        context['mostrar_seccion_desglose'] = bool(context['desglose_presupuesto'])
        context['mostrar_seccion_archivos'] = False  # No hay archivos en tareas
        context['mostrar_seccion_comentarios'] = bool(context['comentarios_recomendaciones'] and context['comentarios_recomendaciones'] != 'Sin comentarios')
        context['mostrar_seccion_validaciones'] = bool(validaciones)
        
        return context
    
    def _get_estado_tarea_display(self, estado):
        """Convierte el código de estado de tarea a texto legible"""
        estados = {
            'PEN': 'Pendiente',
            'EPROG': 'En Progreso',
            'COMPL': 'Completada',
        }
        return estados.get(estado, estado)
    
    def _procesar_validadores(self, validaciones):
        """
        Procesa la lista de validaciones para extraer información de validadores
        """
        validadores = []
        
        for validacion in validaciones:
            validador = validacion.usuarioValidador
            if validador:
                nombre_completo = self._obtener_nombre_completo(validador)
                cargo_real = validador.cargo or 'Sin cargo especificado'
                ci_real = validador.ci or 'N/A'
                
                validadores.append({
                    'nombre': nombre_completo,
                    'cargo': cargo_real,
                    'ci': ci_real,
                    'tipo': cargo_real,
                    'estado': validacion.estado,
                    'estado_display': self._get_estado_display(validacion.estado),
                    'codigo_seguimiento': validacion.codigoSeguimiento,
                    'fecha_asignacion': self._formatear_fecha_hora(validacion.fechaAsignacion),
                    'fecha_resolucion': self._formatear_fecha_hora(validacion.fechaResolucion) if validacion.fechaResolucion else 'Pendiente',
                    'comentarios': validacion.comentarios or 'Sin comentarios',
                    'version_documento': validacion.versionDocumento,
                })
        
        return validadores
    
    def _procesar_desglose_presupuesto(self, desglose):
        """
        Procesa el desglose de presupuesto específico de tarea
        Retorna items con porcentajes precalculados
        """
        if not desglose:
            return [], {}
        
        items = []
        totales = {
            'total_planificado': 0,
            'total_ejecutado': 0,
            'porcentaje_ejecucion': 0,
            'observaciones': '',
            'diferencia': 0
        }
        
        try:
            # Si es diccionario (como en los datos de ejemplo)
            if isinstance(desglose, dict):
                # Extraer items del desglose
                items_desglose = desglose.get('itemsDesglose', [])
                if isinstance(items_desglose, list):
                    for item in items_desglose:
                        if isinstance(item, dict):
                            monto_planificado = float(item.get('monto', 0))
                            monto_ejecutado = float(item.get('montoEjecutado', monto_planificado))
                            
                            # Calcular porcentaje aquí para evitar filtro div en template
                            porcentaje = 0
                            if monto_planificado > 0:
                                porcentaje = round((monto_ejecutado / monto_planificado) * 100, 1)
                            
                            items.append({
                                'concepto': item.get('descripcion', 'Sin concepto'),
                                'monto_planificado': monto_planificado,
                                'monto_ejecutado': monto_ejecutado,
                                'porcentaje': porcentaje,
                                'verificado': item.get('verificado', False),
                                'observaciones': '',
                            })
                
                # Obtener totales del desglose
                total_planificado = float(desglose.get('totalPlanificado', 0)) or float(desglose.get('presupuestoFinal', 0))
                total_ejecutado = float(desglose.get('totalEjecutado', 0)) or float(desglose.get('presupuestoEjecutado', 0))
                
                totales = {
                    'total_planificado': total_planificado,
                    'total_ejecutado': total_ejecutado,
                    'porcentaje_ejecucion': desglose.get('porcentajeEjecucion', '0'),
                    'observaciones': desglose.get('observaciones', ''),
                    'diferencia': float(desglose.get('diferenciaTotal', 0))
                }
                
                # Si no hay items pero hay totales, crear un item resumen
                if not items and total_planificado > 0:
                    porcentaje = 0
                    if total_planificado > 0:
                        porcentaje = round((total_ejecutado / total_planificado) * 100, 1)
                    
                    items.append({
                        'concepto': 'Presupuesto total',
                        'monto_planificado': total_planificado,
                        'monto_ejecutado': total_ejecutado,
                        'porcentaje': porcentaje,
                        'verificado': True,
                        'observaciones': totales['observaciones'],
                    })
            
            # Si es lista (formato antiguo)
            elif isinstance(desglose, list):
                for item in desglose:
                    if isinstance(item, dict):
                        monto_planificado = float(item.get('monto', 0))
                        monto_ejecutado = float(item.get('montoEjecutado', monto_planificado))
                        
                        # Calcular porcentaje aquí
                        porcentaje = 0
                        if monto_planificado > 0:
                            porcentaje = round((monto_ejecutado / monto_planificado) * 100, 1)
                        
                        items.append({
                            'concepto': item.get('concepto', item.get('descripcion', 'Sin concepto')),
                            'monto_planificado': monto_planificado,
                            'monto_ejecutado': monto_ejecutado,
                            'porcentaje': porcentaje,
                            'verificado': item.get('verificado', True),
                            'observaciones': item.get('observaciones', ''),
                        })
                
                # Calcular totales para lista
                if items:
                    totales['total_planificado'] = sum(i['monto_planificado'] for i in items)
                    totales['total_ejecutado'] = sum(i['monto_ejecutado'] for i in items)
                    if totales['total_planificado'] > 0:
                        totales['porcentaje_ejecucion'] = round((totales['total_ejecutado'] / totales['total_planificado']) * 100, 2)
                    totales['diferencia'] = totales['total_planificado'] - totales['total_ejecutado']
                    
        except Exception as e:
            logger.error(f"Error procesando desglose presupuesto: {e}")
            return [], {}
        
        return items, totales
    
    def _procesar_contribucion_proyecto(self, contribucion):
        """Procesa la contribución al proyecto del JSON"""
        if not contribucion:
            return []
        
        items = []
        try:
            if isinstance(contribucion, dict):
                cabecera = contribucion.get('caberaContribucion', {})
                for key, value in cabecera.items():
                    if isinstance(value, dict) and 'data' in value:
                        data = value.get('data', {})
                        items.append({
                            'tipo': key,
                            'codigo': data.get('codigo', ''),
                            'descripcion': data.get('descripcion', ''),
                            'contribucion': data.get('contribucion', ''),
                        })
        except Exception as e:
            logger.error(f"Error procesando contribución: {e}")
        
        return items
    
    def _procesar_avance_indicadores(self, avance):
        """
        Procesa el avance de indicadores del JSON
        Maneja casos donde avance puede ser None
        """
        if avance is None:
            return []
        
        indicadores = []
        try:
            if isinstance(avance, dict):
                for tipo in ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']:
                    items = avance.get(tipo, [])
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                valor = ''
                                if item.get('valor_numerico') is not None:
                                    valor = str(item.get('valor_numerico'))
                                elif item.get('valor_literal'):
                                    valor = item.get('valor_literal')
                                elif item.get('valor_porcentual') is not None:
                                    valor = f"{item.get('valor_porcentual')}%"
                                
                                indicadores.append({
                                    'tipo': tipo,
                                    'valor': valor,
                                    'fecha': self._formatear_fecha(item.get('fecha_registro')),
                                    'observaciones': item.get('observaciones', '-'),
                                    'registrado_por': item.get('registrado_por', ''),
                                })
        except Exception as e:
            logger.error(f"Error procesando avance indicadores: {e}")
        
        return indicadores
    
    def _procesar_informacion_cuantitativa(self, info):
        """
        Procesa la información cuantitativa del JSON
        Maneja casos donde info puede ser None
        Extrae las validaciones para controlar qué secciones mostrar
        """
        # Si es None, retornar diccionario vacío
        if info is None:
            return {}
        
        try:
            if isinstance(info, dict):
                # Extraer validaciones (controlan qué secciones se muestran)
                validaciones = info.get('validaciones', {})
                
                return {
                    'total_participantes': info.get('totalParticipantes', 0),
                    'genero': info.get('genero', {}),
                    'edades': info.get('edades', {}),
                    'discapacidad': info.get('discapacidad', {}),
                    'ocupaciones': info.get('ocupaciones', {}),
                    'localidades': info.get('localidades', {}),
                    'organizaciones': info.get('organizaciones', {}),
                    'estadisticas': info.get('estadisticas', {}),
                    'validaciones': validaciones,
                    'seccion_habilitada': info.get('seccionHabilitada', False),
                    'estado': info.get('estado', ''),
                }
        except Exception as e:
            logger.error(f"Error procesando info cuantitativa: {e}")
        
        return {}
    
    def _procesar_herramientas_evaluacion(self, herramientas):
        """Procesa las herramientas de evaluación del JSON"""
        if not herramientas:
            return []
        
        items = []
        try:
            if isinstance(herramientas, dict):
                datos_completos = herramientas.get('datosCompletos', {})
                herramientas_list = datos_completos.get('herramientas', [])
                if isinstance(herramientas_list, list):
                    for item in herramientas_list:
                        if isinstance(item, dict):
                            items.append({
                                'descripcion': item.get('descripcion', ''),
                                'resultado': item.get('resultado', ''),
                            })
        except Exception as e:
            logger.error(f"Error procesando herramientas: {e}")
        
        return items
    
    def _es_instancia_valida(self, obj):
        """Verifica si el objeto es una instancia válida"""
        try:
            from spme_monitoreo.models import InformeTareaPrincipal
            return isinstance(obj, InformeTareaPrincipal)
        except ImportError:
            return False
    
    def _obtener_numero_informe(self, obj):
        return obj.numeroInforme or "S/N"
    
    def _obtener_objetivo_tarea(self, obj):
        return obj.objetivoTarea or 'No especificado'
    
    def _obtener_informe_objetivo_tarea(self, obj):
        return obj.informeObjetivoTarea or 'No especificado'
    
    def _obtener_comentarios(self, obj):
        return obj.comentariosRecomendaciones or 'Sin comentarios'
    
    def _formatear_fecha(self, fecha):
        if not fecha:
            return 'No especificada'
        try:
            return fecha.strftime('%d/%m/%Y')
        except:
            return str(fecha)
    
    def _formatear_fecha_hora(self, fecha):
        if not fecha:
            return 'No registrado'
        try:
            return fecha.strftime('%d/%m/%Y %H:%M')
        except:
            return str(fecha)
    
    def _formatear_monto(self, monto):
        if monto is None:
            return 0.00
        try:
            return float(monto)
        except (ValueError, TypeError):
            return 0.00
    
    def _obtener_nombre_completo(self, usuario):
        if not usuario:
            return ''
        
        partes = []
        if hasattr(usuario, 'nombre') and usuario.nombre:
            partes.append(usuario.nombre)
        if hasattr(usuario, 'paterno') and usuario.paterno:
            partes.append(usuario.paterno)
        if hasattr(usuario, 'materno') and usuario.materno:
            partes.append(usuario.materno)
        
        return ' '.join(partes) if partes else 'Nombre no disponible'
    
    def _get_estado_display(self, estado):
        estados = {
            'PENDIENTE': 'Pendiente',
            'APROBADO': 'Aprobado',
            'RECHAZADO': 'Rechazado',
        }
        return estados.get(estado, estado)
    
    def _calcular_porcentaje_ejecucion(self, obj):
        planificado = self._formatear_monto(obj.presupuestoPlanificado)
        ejecutado = self._formatear_monto(obj.presupuestoEjecutado)
        
        if planificado and planificado > 0 and ejecutado:
            return round((ejecutado / planificado) * 100, 2)
        return 0
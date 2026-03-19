"""
Generador de PDF para Informe de Actividad Principal.
Utiliza el modelo ValidacionInformeActividad para obtener:
- Redactor (usuarioRedactor de la validación)
- Validadores (múltiples, desde las validaciones asociadas)
- Estados de validación
"""

from .pdf_base import BasePDFGenerator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InformeActividadPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Informe de Actividad Principal
    Obtiene redactor y validadores desde el modelo ValidacionInformeActividad
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/informe_actividad_template.html'
        self.sufijo = 'PRINCIPAL'
    
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
        Prepara el contexto específico para Informe de Actividad
        Utiliza las validaciones asociadas al informe
        """
        # Importar aquí para evitar dependencias circulares
        from spme_validaciones.models import ValidacionInformeActividad
        
        if not self._es_instancia_valida(obj):
            raise ValueError("El objeto debe ser una instancia de InformeActividadPrincipal")
        
        # Obtener todas las validaciones asociadas a este informe
        validaciones = list(
            ValidacionInformeActividad.objects.filter(
                informe=obj
            ).select_related(
                'usuarioValidador',
                'usuarioRedactor'
            ).order_by('fechaAsignacion')
        )
        
        logger.info(f"Se encontraron {len(validaciones)} validaciones para el informe {obj.id}")
        
        # Obtener redactor (es el mismo para todas las validaciones)
        redactor = None
        if validaciones:
            redactor = validaciones[0].usuarioRedactor
        
        # Información básica del informe
        context = {
            # Identificación del documento
            'numero_informe': self._obtener_numero_informe(obj),
            'fecha_ejecucion': self._formatear_fecha(obj.fechaEjecucion),
            'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'tipo_documento': 'INFORME DE ACTIVIDAD',
            'subtipo_documento': 'F-IA-01',
            'sufijo_documento': self.sufijo,
            
            # Información de la actividad
            'codigo_actividad': self._obtener_codigo_actividad(obj),
            'nombre_actividad': self._obtener_nombre_actividad(obj),
            'tipo_actividad': self._obtener_tipo_actividad(obj),
            'objetivo_actividad': self._obtener_objetivo_actividad(obj),
            'informe_objetivo': self._obtener_informe_objetivo(obj),
            'descripcion_actividad': self._obtener_descripcion_actividad(obj),
            'estado_actividad': self._obtener_estado_actividad(obj),
            'fecha_programada': self._obtener_fecha_programada(obj),
            
            # Responsable de la actividad
            'responsable_nombre': self._obtener_responsable_nombre(obj),
            'responsable_cargo': self._obtener_responsable_cargo(obj),
            'responsable_ci': self._obtener_responsable_ci(obj),
            
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
            'observaciones_presupuesto': self._obtener_observaciones_presupuesto(obj),
            
            # Metadatos
            'fecha_registro': self._formatear_fecha_hora(obj.timestamp_registro),
            'ultima_modificacion': self._formatear_fecha_hora(obj.timestamp_ultima_modificacion),
            'reporte_tipo': self._obtener_reporte_tipo(obj),
            'comentarios_recomendaciones': self._obtener_comentarios(obj),
        }
        
        # Procesar campos JSON con manejo de null
        context['contribucion_proyecto'] = self._procesar_contribucion_proyecto(obj.contribucionProyecto)
        context['avance_indicadores'] = self._procesar_avance_indicadores(obj.avanceIndicadores)  # Con manejo de null
        context['informacion_cuantitativa'] = self._procesar_informacion_cuantitativa(obj.informacionCuantitativa)
        context['herramientas_evaluacion'] = self._procesar_herramientas_evaluacion(obj.herramientasEvaluacion)
        
        # Procesar procedencia de fondos (maneja null)
        context['procedencia_fondos'] = self._procesar_procedencia_fondos(obj.procedenciaFondos)
        
        # Procesar archivos
        context['medios_verificacion'] = obj.mediosVerificacion or ''
        context['archivos_cuantitativos'] = self._procesar_archivos(obj.archivosCuantitativos, 'cuantitativos')
        context['herramientas_archivos'] = self._procesar_archivos(obj.herramientasArchivos, 'herramientas')
        context['medios_archivos'] = self._procesar_archivos(obj.mediosArchivos, 'medios')
        
        # Añadir totales de fondos al contexto (si existen)
        if hasattr(self, 'total_planificado') and self.total_planificado > 0:
            context['total_fondos_planificado'] = self.total_planificado
            context['total_fondos_ejecutado'] = self.total_ejecutado
            context['porcentaje_ejecucion_fondos'] = self.porcentaje_ejecucion
            context['observaciones_fondos'] = self.observaciones_fondos
            context['mostrar_seccion_fondos'] = True
        else:
            context['total_fondos_planificado'] = 0
            context['total_fondos_ejecutado'] = 0
            context['porcentaje_ejecucion_fondos'] = '0'
            context['observaciones_fondos'] = ''
            context['mostrar_seccion_fondos'] = bool(context['procedencia_fondos'])
        
        # Calcular porcentajes para cada fuente de fondos (para evitar filtro div en template)
        if context['procedencia_fondos']:
            for fuente in context['procedencia_fondos']:
                if fuente['monto_planificado'] > 0:
                    fuente['porcentaje_ejecucion'] = round((fuente['monto_ejecutado'] / fuente['monto_planificado']) * 100, 1)
                else:
                    fuente['porcentaje_ejecucion'] = 0
        
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
        
        # Indicadores de visualización para otras secciones
        context['mostrar_seccion_contribucion'] = bool(context['contribucion_proyecto'])
        context['mostrar_seccion_indicadores'] = bool(context['avance_indicadores'])
        context['mostrar_seccion_herramientas'] = bool(context['herramientas_evaluacion'])
        context['mostrar_seccion_archivos'] = bool(context['archivos_cuantitativos'] or context['herramientas_archivos'] or context['medios_archivos'])
        context['mostrar_seccion_comentarios'] = bool(context['comentarios_recomendaciones'] and context['comentarios_recomendaciones'] != 'Sin comentarios')
        context['mostrar_seccion_validaciones'] = bool(validaciones)
        
        return context
    
    def _procesar_validadores(self, validaciones):
        """
        Procesa la lista de validaciones para extraer información de validadores
        Usa los datos REALES del usuario validador (desde el modelo Usuario)
        """
        validadores = []
        
        for validacion in validaciones:
            validador = validacion.usuarioValidador
            if validador:
                # Obtener datos REALES del usuario
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
    
    def _procesar_procedencia_fondos(self, fondos):
        """
        Procesa la procedencia de fondos del JSON
        Maneja casos donde fondos puede ser None, dict o list
        """
        # Si es None, retornar lista vacía
        if fondos is None:
            return []
        
        items = []
        
        try:
            # Si es diccionario (nuevo formato)
            if isinstance(fondos, dict):
                # Extraer fondos completos
                fondos_completos = fondos.get('fondosCompletos', [])
                if isinstance(fondos_completos, list):
                    for item in fondos_completos:
                        if isinstance(item, dict):
                            items.append({
                                'nombre': item.get('nombre', 'Sin nombre'),
                                'monto_planificado': float(item.get('monto', 0)),
                                'monto_ejecutado': float(item.get('montoEjecutado', 0)),
                                'es_existente': item.get('esExistente', False),
                                'verificado': item.get('verificado', False),
                            })
                
                # Guardar totales
                self.total_planificado = float(fondos.get('totalPlanificado', 0))
                self.total_ejecutado = float(fondos.get('totalEjecutado', 0))
                self.porcentaje_ejecucion = fondos.get('porcentajeEjecucion', '0')
                self.observaciones_fondos = fondos.get('observaciones', '')
            
            # Si es lista (formato antiguo)
            elif isinstance(fondos, list):
                for item in fondos:
                    if isinstance(item, dict):
                        monto = float(item.get('monto', 0))
                        items.append({
                            'nombre': item.get('nombre', 'Sin nombre'),
                            'monto_planificado': monto,
                            'monto_ejecutado': monto,
                            'es_existente': True,
                            'verificado': True,
                        })
                
                # Calcular totales para lista
                if items:
                    self.total_planificado = sum(i['monto_planificado'] for i in items)
                    self.total_ejecutado = self.total_planificado
                    self.porcentaje_ejecucion = '100'
                    self.observaciones_fondos = ''
                        
        except Exception as e:
            logger.error(f"Error procesando fondos: {e}")
            return []
        
        return items
    
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
        # Si es None, retornar lista vacía
        if avance is None:
            return []
        
        indicadores = []
        try:
            if isinstance(avance, dict):
                metadatos = avance.get('metadatos', {})
                for tipo in ['indicadorog', 'indicadoroe', 'indicadorrog', 'indicadorroe']:
                    items = avance.get(tipo, [])
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                # Determinar el valor según el tipo de dato
                                valor = ''
                                if item.get('valor_numerico'):
                                    valor = str(item.get('valor_numerico'))
                                elif item.get('valor_literal'):
                                    valor = item.get('valor_literal')
                                elif item.get('valor_porcentual'):
                                    valor = f"{item.get('valor_porcentual')}%"
                                
                                indicadores.append({
                                    'tipo': tipo,
                                    'nombre': f"{tipo} - {item.get('id_indicador', '')}",
                                    'fecha': self._formatear_fecha(item.get('fecha_registro')),
                                    'valor': valor,
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
    
    def _procesar_medios_verificacion(self, obj):
        """Procesa los medios de verificación del texto"""
        return obj.mediosVerificacion or 'Sin comentarios'
        # if not medios:
        #     return []
        
        # items = []
        # try:
        #     if isinstance(medios, str):
        #         lineas = medios.split('\n')
        #         items = [{'descripcion': linea.strip()} for linea in lineas if linea.strip()]
        # except Exception as e:
        #     logger.error(f"Error procesando medios verificación: {e}")
        
        # return items
    
    def _procesar_archivos(self, archivos, tipo):
        """Procesa los archivos del JSON"""
        if not archivos:
            return []
        
        items = []
        try:
            if isinstance(archivos, list):
                for item in archivos:
                    if isinstance(item, dict):
                        items.append({
                            'nombre': item.get('nombre', 'Archivo sin nombre'),
                        })
        except Exception as e:
            logger.error(f"Error procesando archivos: {e}")
        
        return items
    
    def _es_instancia_valida(self, obj):
        """Verifica si el objeto es una instancia válida"""
        try:
            from spme_monitoreo.models import InformeActividadPrincipal
            return isinstance(obj, InformeActividadPrincipal)
        except ImportError:
            return False
    
    def _obtener_numero_informe(self, obj):
        return obj.numeroInforme or "S/N"
    
    def _obtener_tipo_actividad(self, obj):
        return obj.tipoActividad or 'No especificado'
    
    def _obtener_objetivo_actividad(self, obj):
        return obj.objetivoActividad or 'No especificado'
    
    def _obtener_informe_objetivo(self, obj):
        return obj.informeObjetivoActividad or 'No especificado'
    
    def _obtener_observaciones_presupuesto(self, obj):
        return obj.observacionesPresupuesto or 'Sin observaciones'
    
    def _obtener_reporte_tipo(self, obj):
        return obj.reporteTipo or 'No especificado'
    
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
    
    def _obtener_codigo_actividad(self, obj):
        if obj.actividad:
            return obj.actividad.codigo or 'No asignado'
        return 'No asignado'
    
    def _obtener_nombre_actividad(self, obj):
        if obj.actividad:
            return obj.actividad.nombreCorto or 'No especificado'
        return 'No especificado'
    
    def _obtener_descripcion_actividad(self, obj):
        if obj.actividad:
            return obj.actividad.descripcion or 'No especificada'
        return 'No especificada'
    
    def _obtener_estado_actividad(self, obj):
        if not obj.actividad or not obj.actividad.estado:
            return 'No especificado'
        
        estados = {
            'CRD': 'Creada',
            'PLAN': 'Planificada',
            'RETR': 'Retraso',
            'REPROG': 'Reprogramación',
            'EJEC': 'En Ejecución',
            'REP': 'En Reporte',
            'FIN': 'Finalizado',
        }
        return estados.get(obj.actividad.estado, obj.actividad.estado)
    
    def _obtener_fecha_programada(self, obj):
        if obj.actividad and obj.actividad.fecha_programada:
            return self._formatear_fecha(obj.actividad.fecha_programada)
        return 'No especificada'
    
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
    
    def _obtener_responsable_nombre(self, obj):
        if obj.actividad and obj.actividad.responsable:
            return self._obtener_nombre_completo(obj.actividad.responsable)
        return 'No asignado'
    
    def _obtener_responsable_cargo(self, obj):
        if obj.actividad and obj.actividad.responsable:
            return obj.actividad.responsable.cargo or 'Cargo no especificado'
        return 'No especificado'
    
    def _obtener_responsable_ci(self, obj):
        if obj.actividad and obj.actividad.responsable:
            return obj.actividad.responsable.ci or 'No especificado'
        return 'No especificado'
    
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
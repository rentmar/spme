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
        
        # ===== CONSULTA CORREGIDA =====
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
        
        # ===== OBTENER REDACTOR =====
        redactor = None
        if validaciones:
            redactor = validaciones[0].usuarioRedactor
            logger.info(f"Redactor encontrado: {redactor}")
        
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
        
        # Procesar campos JSON
        context['contribucion_proyecto'] = self._procesar_contribucion_proyecto(obj.contribucionProyecto)
        context['avance_indicadores'] = self._procesar_avance_indicadores(obj.avanceIndicadores)
        context['informacion_cuantitativa'] = self._procesar_informacion_cuantitativa(obj.informacionCuantitativa)
        context['herramientas_evaluacion'] = self._procesar_herramientas_evaluacion(obj.herramientasEvaluacion)
        context['procedencia_fondos'] = self._procesar_procedencia_fondos(obj.procedenciaFondos)
        
        # Procesar archivos
        context['medios_verificacion'] = self._procesar_medios_verificacion(obj.mediosVerificacion)
        context['archivos_cuantitativos'] = self._procesar_archivos(obj.archivosCuantitativos, 'cuantitativos')
        context['herramientas_archivos'] = self._procesar_archivos(obj.herramientasArchivos, 'herramientas')
        context['medios_archivos'] = self._procesar_archivos(obj.mediosArchivos, 'medios')
        
        # Indicadores de visualización
        context['mostrar_seccion_contribucion'] = bool(context['contribucion_proyecto'])
        context['mostrar_seccion_indicadores'] = bool(context['avance_indicadores'])
        context['mostrar_seccion_cuantitativa'] = bool(context['informacion_cuantitativa'])
        context['mostrar_seccion_herramientas'] = bool(context['herramientas_evaluacion'])
        context['mostrar_seccion_fondos'] = bool(context['procedencia_fondos'])
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
                    'cargo': cargo_real,              # ← CARGO REAL del usuario
                    'ci': ci_real,                     # ← CI REAL del usuario
                    'tipo': cargo_real,                # ← TIPO = CARGO REAL (o puedes poner un valor fijo)
                    'estado': validacion.estado,
                    'estado_display': self._get_estado_display(validacion.estado),
                    'codigo_seguimiento': validacion.codigoSeguimiento,
                    'fecha_asignacion': self._formatear_fecha_hora(validacion.fechaAsignacion),
                    'fecha_resolucion': self._formatear_fecha_hora(validacion.fechaResolucion) if validacion.fechaResolucion else 'Pendiente',
                    'comentarios': validacion.comentarios or 'Sin comentarios',
                    'version_documento': validacion.versionDocumento,
                })
        
        return validadores
    
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
    
    def _procesar_contribucion_proyecto(self, contribucion):
        if not contribucion:
            return []
        
        items = []
        try:
            if isinstance(contribucion, list):
                for item in contribucion:
                    if isinstance(item, dict):
                        items.append({
                            'descripcion': item.get('descripcion', 'Sin descripción'),
                            'impacto': item.get('impacto', 'No especificado'),
                            'nivel': item.get('nivel', 'Medio'),
                        })
            elif isinstance(contribucion, dict):
                items.append({
                    'descripcion': contribucion.get('descripcion', 'Sin descripción'),
                    'impacto': contribucion.get('impacto', 'No especificado'),
                    'nivel': contribucion.get('nivel', 'Medio'),
                })
        except Exception as e:
            logger.error(f"Error procesando contribución: {e}")
        
        return items
    
    def _procesar_avance_indicadores(self, avance):
        if not avance:
            return []
        
        indicadores = []
        try:
            if isinstance(avance, list):
                for item in avance:
                    if isinstance(item, dict):
                        indicadores.append({
                            'nombre': item.get('nombre', 'Sin nombre'),
                            'valor_esperado': item.get('valorEsperado', 'No especificado'),
                            'valor_alcanzado': item.get('valorAlcanzado', 'No especificado'),
                            'porcentaje': float(item.get('porcentaje', 0)),
                            'observaciones': item.get('observaciones', '-'),
                        })
            elif isinstance(avance, dict):
                indicadores.append({
                    'nombre': avance.get('nombre', 'Sin nombre'),
                    'valor_esperado': avance.get('valorEsperado', 'No especificado'),
                    'valor_alcanzado': avance.get('valorAlcanzado', 'No especificado'),
                    'porcentaje': float(avance.get('porcentaje', 0)),
                    'observaciones': avance.get('observaciones', '-'),
                })
        except Exception as e:
            logger.error(f"Error procesando avance indicadores: {e}")
        
        return indicadores
    
    def _procesar_informacion_cuantitativa(self, info):
        if not info:
            return []
        
        items = []
        try:
            if isinstance(info, list):
                for item in info:
                    if isinstance(item, dict):
                        items.append({
                            'indicador': item.get('indicador', 'Sin indicador'),
                            'valor': item.get('valor', 'No especificado'),
                            'unidad': item.get('unidad', 'unidades'),
                            'periodo': item.get('periodo', 'No especificado'),
                        })
            elif isinstance(info, dict):
                items.append({
                    'indicador': info.get('indicador', 'Sin indicador'),
                    'valor': info.get('valor', 'No especificado'),
                    'unidad': info.get('unidad', 'unidades'),
                    'periodo': info.get('periodo', 'No especificado'),
                })
        except Exception as e:
            logger.error(f"Error procesando info cuantitativa: {e}")
        
        return items
    
    def _procesar_herramientas_evaluacion(self, herramientas):
        if not herramientas:
            return []
        
        items = []
        try:
            if isinstance(herramientas, list):
                for item in herramientas:
                    if isinstance(item, dict):
                        items.append({
                            'nombre': item.get('nombre', 'Sin nombre'),
                            'descripcion': item.get('descripcion', 'Sin descripción'),
                            'fecha_aplicacion': item.get('fechaAplicacion', 'No especificada'),
                            'resultados': item.get('resultados', 'No especificados'),
                        })
            elif isinstance(herramientas, dict):
                items.append({
                    'nombre': herramientas.get('nombre', 'Sin nombre'),
                    'descripcion': herramientas.get('descripcion', 'Sin descripción'),
                    'fecha_aplicacion': herramientas.get('fechaAplicacion', 'No especificada'),
                    'resultados': herramientas.get('resultados', 'No especificados'),
                })
        except Exception as e:
            logger.error(f"Error procesando herramientas: {e}")
        
        return items
    
    def _procesar_procedencia_fondos(self, fondos):
        if not fondos:
            return []
        
        items = []
        total = 0
        
        try:
            if isinstance(fondos, list):
                for item in fondos:
                    if isinstance(item, dict):
                        monto = float(item.get('monto', 0))
                        items.append({
                            'nombre': item.get('nombre', 'Sin nombre'),
                            'monto': monto,
                        })
                        total += monto
            elif isinstance(fondos, dict):
                monto = float(fondos.get('monto', 0))
                items.append({
                    'nombre': fondos.get('nombre', 'Sin nombre'),
                    'monto': monto,
                })
                total = monto
            
            if total > 0:
                for item in items:
                    item['porcentaje'] = round((item['monto'] / total) * 100, 2)
            else:
                for item in items:
                    item['porcentaje'] = 0
                    
        except Exception as e:
            logger.error(f"Error procesando fondos: {e}")
        
        return items
    
    def _procesar_medios_verificacion(self, medios):
        if not medios:
            return []
        
        items = []
        try:
            if isinstance(medios, str):
                lineas = medios.split('\n')
                items = [{'descripcion': linea.strip()} for linea in lineas if linea.strip()]
            elif isinstance(medios, list):
                for medio in medios:
                    if isinstance(medio, str):
                        items.append({'descripcion': medio})
                    elif isinstance(medio, dict):
                        items.append({'descripcion': medio.get('descripcion', 'Medio de verificación')})
        except Exception as e:
            logger.error(f"Error procesando medios verificación: {e}")
        
        return items
    
    def _procesar_archivos(self, archivos, tipo):
        if not archivos:
            return []
        
        items = []
        try:
            if isinstance(archivos, list):
                for item in archivos:
                    if isinstance(item, dict):
                        items.append({
                            'nombre': item.get('nombre', 'Archivo sin nombre'),
                            'tipo': item.get('tipo', tipo),
                            'tamano': item.get('tamano', 'N/A'),
                            'fecha': item.get('fecha', 'No especificada'),
                        })
                    elif isinstance(item, str):
                        items.append({
                            'nombre': item,
                            'tipo': tipo,
                            'tamano': 'N/A',
                            'fecha': 'No especificada',
                        })
        except Exception as e:
            logger.error(f"Error procesando archivos: {e}")
        
        return items
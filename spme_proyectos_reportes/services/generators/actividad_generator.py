# services/generators/actividad_generator.py
from ..base.actividad_base_service import ActividadBaseReportService
from spme_actividades.models import Actividad
from spme_monitoreo.models import InfActividad, InfTarea
from spme_actividades.models import TareaActividad
import json
import logging

class ActividadGenerator(ActividadBaseReportService):
    """Generador de reportes para actividades - CON INFORMES COMPLETOS Y SUBACTIVIDADES"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def generar_reporte_actividad(self, actividad_id):
        """Genera el reporte de actividad con informes relacionados y subactividades"""
        try:
            actividad = Actividad.objects.select_related(
                'proyecto',
                'responsable',
                'tipo'
            ).get(id=actividad_id)
            
            # Generar secciones en orden
            secciones = [
                ('Portada', self._agregar_portada),
                ('Información Básica', self._agregar_informacion_basica),
                ('Fechas y Estado', self._agregar_fechas_estado),
                ('Presupuesto', self._agregar_presupuesto),
                ('Descripciones', self._agregar_descripciones),
                ('Análisis de Riesgos', self._agregar_analisis_riesgos),
                ('Estructura Organizativa', self._agregar_estructura_organizativa),
                ('Estructura de Procedencia', self._agregar_estructura_procedencia),
                ('Informes de Actividad', self._agregar_informes_actividad),
                ('Subactividades', self._agregar_subactividades)  # NUEVA SECCIÓN
            ]
            
            for nombre_seccion, metodo in secciones:
                try:
                    metodo(actividad)
                except Exception as e:
                    self.agregar_parrafo(f"Error en sección {nombre_seccion}: {str(e)}")
                    self.logger.error(f"Error en sección {nombre_seccion}: {str(e)}")
                    continue
                
            return self.guardar_documento()
            
        except Actividad.DoesNotExist:
            error_msg = f"Actividad con id {actividad_id} no existe"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error generando reporte: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _agregar_portada(self, actividad):
        """Portada del reporte"""
        self.agregar_titulo_principal('REPORTE DE ACTIVIDAD')
        self.agregar_parrafo(f"Código: {actividad.codigo or 'No definido'}")
        self.agregar_parrafo(f"Nombre: {actividad.nombreCorto or 'Sin nombre'}")
        self.agregar_parrafo(f"Fecha de generación: {self.obtener_fecha_actual()}")
        self.agregar_parrafo("")
    
    def _agregar_informacion_basica(self, actividad):
        """Información básica de la actividad"""
        self.agregar_seccion('1. INFORMACIÓN BÁSICA', 1)
        
        datos_basicos = [
            ('Código', actividad.codigo),
            ('Nombre Corto', actividad.nombreCorto),
            ('Tipo de Actividad', actividad.tipo.tipo_actividad if actividad.tipo else None),
            ('Sigla Tipo', actividad.tipo.sigla if actividad.tipo else None),
            ('Estado', actividad.get_estado_display()),
            ('Responsable', f"{actividad.responsable.get_full_name()}" if actividad.responsable else None),
            ('Actividad Inactiva', 'Sí' if actividad.estaInactiva else 'No')
        ]
        
        self.agregar_tabla_clave_valor(datos_basicos, 'Datos Principales')
    
    def _agregar_fechas_estado(self, actividad):
        """Fechas y estado de la actividad"""
        self.agregar_seccion('2. FECHAS Y ESTADO', 1)
        
        datos_fechas = [
            ('Fecha Programada', self.formatear_fecha(actividad.fecha_programada)),
            ('Fecha de Inicio', self.formatear_fecha(actividad.fecha_inicio)),
            ('Fecha de Cierre', self.formatear_fecha(actividad.fecha_cierre)),
            ('Grado de Ejecución', actividad.gradoEjecucion)
        ]
        
        self.agregar_tabla_clave_valor(datos_fechas, 'Cronograma')
    
    def _agregar_presupuesto(self, actividad):
        """Información presupuestaria"""
        self.agregar_seccion('3. INFORMACIÓN PRESUPUESTARIA', 1)
        
        # Calcular saldo (Presupuesto - Total Reportado)
        presupuesto = actividad.presupuesto or 0
        total_reportado = actividad.totalReportado or 0
        saldo = presupuesto - total_reportado
        
        datos_presupuesto = [
            ('Presupuesto', self.formatear_moneda(presupuesto)),
            ('Total Reportado', self.formatear_moneda(total_reportado)),
            ('Saldo', self.formatear_moneda(saldo))
        ]
        
        self.agregar_tabla_clave_valor(datos_presupuesto, 'Estado Financiero')
        
        # Procedencia de fondos
        if actividad.procedencia_fondos:
            self.agregar_seccion('Procedencia de Fondos', 2)
            
            datos_fondos = []
            for fondo in actividad.procedencia_fondos:
                nombre = fondo.get('nombre', 'No definido')
                monto = fondo.get('monto', 0)
                es_manual = fondo.get('manual', False)
                fuente = f"{nombre} {'(Manual)' if es_manual else ''}"
                datos_fondos.append([fuente, self.formatear_moneda(monto)])
            
            # Crear tabla para fondos
            tabla_fondos = self.document.add_table(rows=len(datos_fondos) + 1, cols=2)
            tabla_fondos.style = 'Light Grid Accent 2'
            
            # Encabezados
            tabla_fondos.cell(0, 0).text = 'Fuente de Financiamiento'
            tabla_fondos.cell(0, 1).text = 'Monto'
            tabla_fondos.cell(0, 0).paragraphs[0].runs[0].bold = True
            tabla_fondos.cell(0, 1).paragraphs[0].runs[0].bold = True
            
            # Datos
            for i, (fuente, monto) in enumerate(datos_fondos, 1):
                tabla_fondos.cell(i, 0).text = fuente
                tabla_fondos.cell(i, 1).text = monto
            
            self.agregar_parrafo("")
    
    def _agregar_descripciones(self, actividad):
        """Descripciones detalladas"""
        tiene_descripciones = any([
            actividad.descripcion,
            actividad.objetivo_de_actividad,
            actividad.descripcion_evaluacion,
            actividad.descripcion_tipo_actividad
        ])
        
        if tiene_descripciones:
            self.agregar_seccion('4. DESCRIPCIÓN Y PLANIFICACIÓN', 1)
            
            if actividad.descripcion:
                self.agregar_seccion('Descripción General', 2)
                self.agregar_parrafo(actividad.descripcion)
                self.agregar_parrafo("")
            
            if actividad.objetivo_de_actividad:
                self.agregar_seccion('Objetivo de la Actividad', 2)
                self.agregar_parrafo(actividad.objetivo_de_actividad)
                self.agregar_parrafo("")
            
            if actividad.descripcion_evaluacion:
                self.agregar_seccion('Planificación y Evaluación', 2)
                self.agregar_parrafo(actividad.descripcion_evaluacion)
                self.agregar_parrafo("")
            
            if actividad.descripcion_tipo_actividad:
                self.agregar_seccion('Descripción del Tipo de Actividad', 2)
                self.agregar_parrafo(actividad.descripcion_tipo_actividad)
                self.agregar_parrafo("")
    
    def _agregar_analisis_riesgos(self, actividad):
        """Análisis de riesgos y supuestos"""
        tiene_analisis = any([
            actividad.riesgos,
            actividad.supuestos,
            actividad.factoresCriticos
        ])
        
        if tiene_analisis:
            self.agregar_seccion('5. ANÁLISIS Y RIESGOS', 1)
            
            if actividad.supuestos:
                self.agregar_seccion('Supuestos', 2)
                self.agregar_parrafo(actividad.supuestos)
                self.agregar_parrafo("")
            
            if actividad.riesgos:
                self.agregar_seccion('Riesgos Identificados', 2)
                self.agregar_parrafo(actividad.riesgos)
                self.agregar_parrafo("")
            
            if actividad.factoresCriticos:
                self.agregar_seccion('Factores Críticos', 2)
                if isinstance(actividad.factoresCriticos, list):
                    for factor in actividad.factoresCriticos:
                        if isinstance(factor, dict):
                            nombre = factor.get('nombre', 'Factor')
                            descripcion = factor.get('descripcion', '')
                            self.agregar_parrafo(f"• {nombre}: {descripcion}")
                        else:
                            self.agregar_parrafo(f"• {factor}")
                else:
                    self.agregar_parrafo(str(actividad.factoresCriticos))
                self.agregar_parrafo("")
    
    def _agregar_estructura_organizativa(self, actividad):
        """Estructura organizativa"""
        tiene_estructura = any([
            actividad.proyecto,
            actividad.rutaTrazadoIndicadores,
        ])
        
        if tiene_estructura:
            self.agregar_seccion('6. ESTRUCTURA ORGANIZATIVA', 1)
            
            if actividad.proyecto:
                datos_proyecto = [
                    ('Proyecto Asociado', actividad.proyecto.codigo),
                    ('Título del Proyecto', actividad.proyecto.titulo)
                ]
                self.agregar_tabla_clave_valor(datos_proyecto, 'Vinculación con Proyecto')
            
            if actividad.rutaTrazadoIndicadores:
                self.agregar_seccion('Ruta de Trazado de Indicadores', 2)
                self.agregar_parrafo("Información de trazado de indicadores disponible en el sistema.")
                self.agregar_parrafo("")
    
    def _agregar_estructura_procedencia(self, actividad):
        """ESTRUCTURA DE PROCEDENCIA - Solo tipo y código"""
        if not actividad.estructuraProcedencia:
            return
            
        self.agregar_seccion('7. ESTRUCTURA DE PROCEDENCIA', 1)
        
        estructura = actividad.estructuraProcedencia
        datos_procedencia = estructura.get('datosProcedencia', {})
        
        # Crear tabla con todos los elementos
        elementos_vinculados = []
        
        # Procesar cada tipo de elemento
        elementos_vinculados.extend(self._obtener_elementos_simple(datos_procedencia, 'objetivogeneral'))
        elementos_vinculados.extend(self._obtener_elementos_simple(datos_procedencia, 'objetivoespecificoog'))
        elementos_vinculados.extend(self._obtener_elementos_lista(datos_procedencia, 'indicadoroe'))
        elementos_vinculados.extend(self._obtener_elementos_simple(datos_procedencia, 'resultadooe'))
        elementos_vinculados.extend(self._obtener_elementos_lista(datos_procedencia, 'indicadorroe'))
        
        if elementos_vinculados:
            # Crear tabla con tipo y código
            tabla = self.document.add_table(rows=len(elementos_vinculados) + 1, cols=2)
            tabla.style = 'Light Grid Accent 1'
            
            # Encabezados
            tabla.cell(0, 0).text = 'Tipo'
            tabla.cell(0, 1).text = 'Código'
            tabla.cell(0, 0).paragraphs[0].runs[0].bold = True
            tabla.cell(0, 1).paragraphs[0].runs[0].bold = True
            
            # Datos
            for i, (tipo, codigo) in enumerate(elementos_vinculados, 1):
                tabla.cell(i, 0).text = tipo
                tabla.cell(i, 1).text = codigo
            
            self.agregar_parrafo("")
        else:
            self.agregar_parrafo("No hay elementos vinculados en la estructura de procedencia.")
            self.agregar_parrafo("")
    
    def _agregar_informes_actividad(self, actividad):
        """SECCIÓN: Informes de actividad relacionados - VERSIÓN CORREGIDA"""
        try:
            # Obtener informes con manejo seguro
            informes = InfActividad.objects.filter(actividad=actividad).order_by('fecha_ejecucion')
            
            if not informes.exists():
                self.agregar_parrafo("No hay informes de actividad registrados.")
                return
                
            self.agregar_seccion('8. INFORMES DE ACTIVIDAD', 1)
            total_informes = len(informes)
            
            for i, informe in enumerate(informes, 1):
                try:
                    self._agregar_informe_individual(informe, i)
                    
                    # Agregar separador solo si no es el último informe
                    if i < total_informes:
                        self.agregar_parrafo("―" * 80)
                        self.agregar_parrafo("")
                        
                except Exception as e:
                    error_msg = f"Error procesando informe {i}: {str(e)}"
                    self.agregar_parrafo(error_msg)
                    self.logger.error(error_msg)
                    continue
                    
        except Exception as e:
            error_msg = f"Error al cargar informes de actividad: {str(e)}"
            self.agregar_parrafo(error_msg)
            self.logger.error(error_msg)
    
    def _agregar_subactividades(self, actividad):
        """NUEVA SECCIÓN 9: Subactividades (Tareas) relacionadas"""
        try:
            # Obtener subactividades (tareas) relacionadas
            subactividades = TareaActividad.objects.filter(actividad=actividad).order_by('fecha_creacion')
            
            if not subactividades.exists():
                self.agregar_parrafo("No hay subactividades registradas para esta actividad.")
                return
                
            self.agregar_seccion('9. SUBACTIVIDADES', 1)
            total_subactividades = len(subactividades)
            
            for i, subactividad in enumerate(subactividades, 1):
                try:
                    self._agregar_subactividad_individual(subactividad, i)
                    
                    # Agregar separador solo si no es la última subactividad
                    if i < total_subactividades:
                        self.agregar_parrafo("―" * 80)
                        self.agregar_parrafo("")
                        
                except Exception as e:
                    error_msg = f"Error procesando subactividad {i}: {str(e)}"
                    self.agregar_parrafo(error_msg)
                    self.logger.error(error_msg)
                    continue
                    
        except Exception as e:
            error_msg = f"Error al cargar subactividades: {str(e)}"
            self.agregar_parrafo(error_msg)
            self.logger.error(error_msg)
    
    def _agregar_subactividad_individual(self, subactividad, numero):
        """Agrega una subactividad individual al documento"""
        # Título de la subactividad
        titulo_subactividad = f'Subactividad {numero}'
        if subactividad.codigo:
            titulo_subactividad += f': {subactividad.codigo}'
        
        self.agregar_seccion(titulo_subactividad, 2)
        
        # Información básica de la subactividad
        datos_basicos = [
            ('Código', subactividad.codigo or 'No definido'),
            ('Título', subactividad.titulo or 'Sin título'),
            ('Estado', subactividad.get_estado_display()),
            ('Fecha de Creación', self.formatear_fecha(subactividad.fecha_creacion)),
            ('Fecha de Ejecución', self.formatear_fecha(subactividad.fecha_ejecucion)),
            ('Fecha Límite', self.formatear_fecha(subactividad.fecha_limite)),
            ('Presupuesto', self.formatear_moneda(subactividad.presupuesto)),
        ]
        
        self.agregar_tabla_clave_valor(datos_basicos, 'Información de la Subactividad')
        
        # Descripción de la subactividad
        if subactividad.descripcion:
            self.agregar_seccion('Descripción', 3)
            self.agregar_parrafo(subactividad.descripcion)
            self.agregar_parrafo("")
        
        # Desglose de presupuesto
        if subactividad.presupuestoDesglose:
            self._agregar_desglose_presupuesto_subactividad(subactividad.presupuestoDesglose)
        
        # Informes de la subactividad
        self._agregar_informes_subactividad(subactividad)
    
    def _agregar_desglose_presupuesto_subactividad(self, presupuesto_desglose):
        """Agrega el desglose de presupuesto de la subactividad"""
        self.agregar_seccion('Desglose de Presupuesto', 3)
        
        try:
            if isinstance(presupuesto_desglose, dict):
                datos_desglose = []
                for clave, valor in presupuesto_desglose.items():
                    if valor not in (None, "", 0, "0"):
                        nombre_legible = self._formatear_nombre_campo(clave)
                        if isinstance(valor, (int, float)):
                            valor_formateado = self.formatear_moneda(valor)
                        else:
                            valor_formateado = str(valor)
                        datos_desglose.append((nombre_legible, valor_formateado))
                
                if datos_desglose:
                    self.agregar_tabla_clave_valor(datos_desglose)
                else:
                    self.agregar_parrafo("No hay datos de desglose presupuestario disponibles")
            
            elif isinstance(presupuesto_desglose, list):
                for i, item in enumerate(presupuesto_desglose, 1):
                    if isinstance(item, dict):
                        self.agregar_parrafo(f"Partida {i}:")
                        for clave, valor in item.items():
                            if valor not in (None, "", 0, "0"):
                                nombre_legible = self._formatear_nombre_campo(clave)
                                if isinstance(valor, (int, float)):
                                    valor_formateado = self.formatear_moneda(valor)
                                else:
                                    valor_formateado = str(valor)
                                self.agregar_parrafo(f"  • {nombre_legible}: {valor_formateado}")
                        self.agregar_parrafo("")
                    else:
                        self.agregar_parrafo(f"• {item}")
            else:
                self.agregar_parrafo(str(presupuesto_desglose))
                
        except Exception as e:
            self.agregar_parrafo(f"Error procesando desglose presupuestario: {str(e)}")
            self.logger.error(f"Error procesando desglose presupuestario: {str(e)}")
        
        self.agregar_parrafo("")
    
    def _agregar_informes_subactividad(self, subactividad):
        """Agrega los informes relacionados con la subactividad"""
        try:
            informes = InfTarea.objects.filter(tarea=subactividad).order_by('fecha_ejecucion')
            
            if not informes.exists():
                self.agregar_parrafo("No hay informes registrados para esta subactividad.")
                return
            
            self.agregar_seccion('Informes de la Subactividad', 3)
            total_informes = len(informes)
            
            for i, informe in enumerate(informes, 1):
                try:
                    self._agregar_informe_subactividad_individual(informe, i)
                    
                    # Agregar separador solo si no es el último informe
                    if i < total_informes:
                        self.agregar_parrafo("―" * 50)
                        self.agregar_parrafo("")
                        
                except Exception as e:
                    error_msg = f"Error procesando informe {i} de subactividad: {str(e)}"
                    self.agregar_parrafo(error_msg)
                    self.logger.error(error_msg)
                    continue
                    
        except Exception as e:
            error_msg = f"Error al cargar informes de subactividad: {str(e)}"
            self.agregar_parrafo(error_msg)
            self.logger.error(error_msg)
    
    def _agregar_informe_subactividad_individual(self, informe, numero):
        """Agrega un informe individual de subactividad al documento"""
        # Título del informe
        titulo_informe = f'Informe {numero}'
        if informe.numeroInforme:
            titulo_informe += f': {informe.numeroInforme}'
        
        self.agregar_seccion(titulo_informe, 4)
        
        # Información básica del informe
        datos_basicos = [
            ('Número de Informe', informe.numeroInforme or 'No definido'),
            ('Fecha de Ejecución', self.formatear_fecha(informe.fecha_ejecucion)),
            ('Tipo de Actividad', informe.tipo_actividad or 'No especificado'),
            ('Presupuesto Planificado', self.formatear_moneda(informe.presupuesto_planificado)),
            ('Presupuesto Ejecutado', self.formatear_moneda(informe.presupuesto_ejecutado)),
        ]
        
        self.agregar_tabla_clave_valor(datos_basicos, 'Información del Informe')
        
        # Contribución al proyecto
        if informe.contribucion_proyecto:
            self._agregar_contribucion_proyecto(informe.contribucion_proyecto)
        
        # Avance de indicadores
        if informe.avance_indicadores:
            self._agregar_avance_indicadores(informe.avance_indicadores)
        
        # Desglose de presupuesto del informe
        if informe.desglose_presupuesto:
            self.agregar_seccion('Desglose de Presupuesto del Informe', 5)
            self._procesar_datos_estructurados(informe.desglose_presupuesto, '', 5)
        
        # Secciones de texto específicas de informes de subactividad
        secciones_texto = [
            ('Objetivo de la Subactividad', informe.objetivo_tarea),
            ('Informe del Objetivo', informe.informe_objetivo_tarea),
            ('Información Cuantitativa', informe.informacion_cuantitativa),
            ('Herramientas de Evaluación', informe.herramientas_evaluacion),
            ('Medios de Verificación', informe.medios_verificacion),
            ('Comentarios y Recomendaciones', informe.comentarios_recomendaciones),
        ]
        
        for titulo, contenido in secciones_texto:
            if contenido:
                self.agregar_seccion(titulo, 5)
                self.agregar_parrafo(contenido)
                self.agregar_parrafo("")
    
    def _agregar_informe_individual(self, informe, numero):
        """Agrega un informe individual al documento"""
        # Título del informe
        titulo_informe = f'Informe {numero}'
        if informe.numeroInforme:
            titulo_informe += f': {informe.numeroInforme}'
        
        self.agregar_seccion(titulo_informe, 2)
        
        # Información básica del informe
        datos_basicos = [
            ('Número de Informe', informe.numeroInforme or 'No definido'),
            ('Fecha de Ejecución', self.formatear_fecha(informe.fecha_ejecucion)),
            ('Tipo de Actividad', informe.tipo_actividad or 'No especificado'),
            ('Presupuesto Planificado', self.formatear_moneda(informe.presupuesto_planificado)),
            ('Presupuesto Ejecutado', self.formatear_moneda(informe.presupuesto_ejecutado)),
        ]
        
        self.agregar_tabla_clave_valor(datos_basicos, 'Información del Informe')
        
        # Contribución al proyecto
        if informe.contribucion_proyecto:
            self._agregar_contribucion_proyecto(informe.contribucion_proyecto)
        
        # Avance de indicadores
        if informe.avance_indicadores:
            self._agregar_avance_indicadores(informe.avance_indicadores)
        
        # Secciones de texto
        secciones_texto = [
            ('Objetivo de la Actividad', informe.objetivo_actividad),
            ('Informe del Objetivo', informe.informe_objetivo_actividad),
            ('Información Cuantitativa', informe.informacion_cuantitativa),
            ('Herramientas de Evaluación', informe.herramientas_evaluacion),
            ('Medios de Verificación', informe.medios_verificacion),
            ('Comentarios y Recomendaciones', informe.comentarios_recomendaciones),
            ('Observaciones de Presupuesto', informe.observaciones_presupuesto),
            ('Reporte del Tipo de Actividad', informe.reporte_tipo),
        ]
        
        for titulo, contenido in secciones_texto:
            if contenido:
                self.agregar_seccion(titulo, 3)
                self.agregar_parrafo(contenido)
                self.agregar_parrafo("")
    
    def _agregar_contribucion_proyecto(self, contribucion_proyecto):
        """Agrega información de contribución al proyecto - VERSIÓN MEJORADA"""
        self.agregar_seccion('Contribución al Proyecto', 3)
        
        try:
            # Si es string, intentar parsear como JSON
            if isinstance(contribucion_proyecto, str):
                try:
                    contribucion_proyecto = json.loads(contribucion_proyecto)
                except json.JSONDecodeError:
                    # Si no es JSON válido, mostrar como texto
                    self.agregar_parrafo(contribucion_proyecto)
                    self.agregar_parrafo("")
                    return
            
            if isinstance(contribucion_proyecto, dict):
                self._procesar_diccionario_contribucion(contribucion_proyecto)
            elif isinstance(contribucion_proyecto, list):
                self._procesar_lista_contribucion(contribucion_proyecto)
            else:
                self.agregar_parrafo(str(contribucion_proyecto))
                
        except Exception as e:
            self.agregar_parrafo(f"Error procesando contribución: {str(e)}")
            self.logger.error(f"Error procesando contribución: {str(e)}")
        
        self.agregar_parrafo("")
    
    def _procesar_diccionario_contribucion(self, datos):
        """Procesa datos de contribución en formato diccionario"""
        datos_filtrados = []
        for clave, valor in datos.items():
            if valor not in (None, "", 0, "0"):  # Incluir incluso valores 0
                nombre_legible = self._formatear_nombre_campo(clave)
                datos_filtrados.append((nombre_legible, str(valor)))
        
        if datos_filtrados:
            self.agregar_tabla_clave_valor(datos_filtrados)
        else:
            self.agregar_parrafo("No hay datos de contribución disponibles")
    
    def _procesar_lista_contribucion(self, lista_datos):
        """Procesa datos de contribución en formato lista"""
        for i, item in enumerate(lista_datos, 1):
            if isinstance(item, dict):
                self.agregar_parrafo(f"Contribución {i}:")
                for clave, valor in item.items():
                    if valor not in (None, "", 0, "0"):
                        nombre_legible = self._formatear_nombre_campo(clave)
                        self.agregar_parrafo(f"  • {nombre_legible}: {valor}")
                self.agregar_parrafo("")
            else:
                self.agregar_parrafo(f"• {item}")
    
    def _agregar_avance_indicadores(self, avance_indicadores):
        """Agrega información de avance de indicadores - VERSIÓN MEJORADA"""
        self.agregar_seccion('Avance de Indicadores', 3)
        
        try:
            # Si es string, intentar parsear como JSON
            if isinstance(avance_indicadores, str):
                try:
                    avance_indicadores = json.loads(avance_indicadores)
                except json.JSONDecodeError:
                    # Si no es JSON válido, mostrar como texto
                    self.agregar_parrafo(avance_indicadores)
                    self.agregar_parrafo("")
                    return
            
            if isinstance(avance_indicadores, dict):
                self._procesar_diccionario_avance(avance_indicadores)
            elif isinstance(avance_indicadores, list):
                self._procesar_lista_avance(avance_indicadores)
            else:
                self.agregar_parrafo(str(avance_indicadores))
                
        except Exception as e:
            self.agregar_parrafo(f"Error procesando avance de indicadores: {str(e)}")
            self.logger.error(f"Error procesando avance de indicadores: {str(e)}")
        
        self.agregar_parrafo("")
    
    def _procesar_diccionario_avance(self, datos):
        """Procesa datos de avance en formato diccionario"""
        datos_filtrados = []
        for clave, valor in datos.items():
            if valor is not None:  # Mostrar incluso valores 0
                nombre_legible = self._formatear_nombre_campo(clave)
                datos_filtrados.append((nombre_legible, str(valor)))
        
        if datos_filtrados:
            self.agregar_tabla_clave_valor(datos_filtrados)
        else:
            self.agregar_parrafo("No hay datos de avance de indicadores disponibles")
    
    def _procesar_lista_avance(self, lista_datos):
        """Procesa datos de avance en formato lista"""
        for i, item in enumerate(lista_datos, 1):
            if isinstance(item, dict):
                self.agregar_parrafo(f"Indicador {i}:")
                for clave, valor in item.items():
                    if valor is not None:
                        nombre_legible = self._formatear_nombre_campo(clave)
                        self.agregar_parrafo(f"  • {nombre_legible}: {valor}")
                self.agregar_parrafo("")
            else:
                self.agregar_parrafo(f"• {item}")
    
    def _procesar_datos_estructurados(self, datos, titulo="", nivel=3):
        """Procesa datos estructurados de manera genérica"""
        if titulo:
            self.agregar_seccion(titulo, nivel)
        
        try:
            if isinstance(datos, dict):
                datos_filtrados = []
                for clave, valor in datos.items():
                    if valor not in (None, "", 0, "0"):
                        nombre_legible = self._formatear_nombre_campo(clave)
                        if isinstance(valor, (int, float)):
                            valor_formateado = self.formatear_moneda(valor) if 'presupuesto' in clave.lower() else str(valor)
                        else:
                            valor_formateado = str(valor)
                        datos_filtrados.append((nombre_legible, valor_formateado))
                
                if datos_filtrados:
                    self.agregar_tabla_clave_valor(datos_filtrados)
                else:
                    self.agregar_parrafo("No hay datos disponibles")
            
            elif isinstance(datos, list):
                for i, item in enumerate(datos, 1):
                    if isinstance(item, dict):
                        self.agregar_parrafo(f"Item {i}:")
                        for clave, valor in item.items():
                            if valor not in (None, "", 0, "0"):
                                nombre_legible = self._formatear_nombre_campo(clave)
                                if isinstance(valor, (int, float)):
                                    valor_formateado = self.formatear_moneda(valor) if 'presupuesto' in clave.lower() else str(valor)
                                else:
                                    valor_formateado = str(valor)
                                self.agregar_parrafo(f"  • {nombre_legible}: {valor_formateado}")
                        self.agregar_parrafo("")
                    else:
                        self.agregar_parrafo(f"• {item}")
            else:
                self.agregar_parrafo(str(datos))
                
        except Exception as e:
            self.agregar_parrafo(f"Error procesando datos: {str(e)}")
            self.logger.error(f"Error procesando datos: {str(e)}")
        
        self.agregar_parrafo("")
    
    def _obtener_elementos_simple(self, datos_procedencia, clave):
        """Obtiene elementos individuales (tipo y código)"""
        elementos = []
        elemento = datos_procedencia.get(clave)
        
        if elemento:
            tipo = elemento.get('tipo', clave)
            data = elemento.get('data', {})
            codigo = data.get('codigo', 'No definido')
            elementos.append((tipo, codigo))
        
        return elementos
    
    def _obtener_elementos_lista(self, datos_procedencia, clave):
        """Obtiene elementos en lista (tipo y código)"""
        elementos = []
        elementos_data = datos_procedencia.get(clave, [])
        
        # Si es un diccionario individual, convertirlo a lista
        if isinstance(elementos_data, dict):
            elementos_data = [elementos_data]
        
        for elemento in elementos_data:
            if elemento:  # Verificar que el elemento no sea None o vacío
                tipo = elemento.get('tipo', clave)
                data = elemento.get('data', {})
                codigo = data.get('codigo', 'No definido')
                elementos.append((tipo, codigo))
        
        return elementos
    
    def _formatear_nombre_campo(self, clave):
        """Formatea nombres de campos para mejor presentación"""
        # Reemplazar guiones bajos y capitalizar
        return clave.replace('_', ' ').title()
    
    def formatear_moneda(self, valor):
        """Formatea valores monetarios"""
        if valor is None:
            return "No definido"
        try:
            return f"${float(valor):,.2f}"
        except (TypeError, ValueError):
            return "Formato inválido"
    
    def formatear_fecha(self, fecha):
        """Formatea fechas"""
        if not fecha:
            return "No definida"
        return fecha.strftime("%d/%m/%Y")
    
    def obtener_fecha_actual(self):
        """Retorna la fecha actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def _debug_informes(self, informes):
        """Método para debug de informes"""
        print(f"Total informes: {len(informes)}")
        for i, informe in enumerate(informes):
            print(f"Informe {i}: {type(informe)} - {informe}")
            print(f"  ID: {informe.id}")
            print(f"  Numero: {informe.numeroInforme}")
            print(f"  Tipo: {type(informe.numeroInforme)}")
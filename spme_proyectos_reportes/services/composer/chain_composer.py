from django.http import HttpResponse
import os
import django
import logging

# Configurar Django explícitamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

from spme_estructuracion_proyecto.models import (
    Proyecto, 
    ObjetivoGeneralProyecto, 
    ObjetivoEspecificoProyecto,
    ResultadoOG,
    ResultadoOE,
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    IndicadorObjetivoEspecifico,
    ProductoOE,
    Proceso,
    IndicadorResultadoObjEspecifico,
    ProductoResultadoOE,
)
from spme_actividades.models import Actividad, TareaActividad
from spme_monitoreo.models import InfActividad, InfTarea

from ..generators.proyecto_generator import ProyectoGenerator
from ..generators.objetivo_general_generator import ObjetivoGeneralGenerator
from ..generators.objetivo_especifico_og_generator import ObjetivoEspecificoOGGenerator
from ..generators.resultado_og_generator import ResultadoOGGenerator
from ..generators.indicador_og_generator import IndicadorOGGenerator
from ..generators.indicador_rog_generator import IndicadorROGGenerator
from ..generators.indicador_oe_generator import IndicadorOEGenerator
from ..generators.resultado_oe_generator import ResultadoOEGenerator
from ..generators.producto_oe_generator import ProductoOEGenerator 
from ..generators.indicador_roe_generator import IndicadorROEGenerator
from ..generators.producto_roe_generator import ProductoROEGenerator
from ..generators.proceso_generator import ProcesoGenerator
from ..generators.actividad_generator import ActividadGenerator


class ChainComposer:
    """
    Orquestador principal para encadenamiento de reportes con actividades vinculadas a la jerarquía
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generators_registry = {
            'proyecto': {
                'generator_class': ProyectoGenerator,
                'nivel': 1
            },
            'objetivogeneral': {
                'generator_class': ObjetivoGeneralGenerator, 
                'nivel': 2
            },
            'objetivoespecificoog': {
                'generator_class': ObjetivoEspecificoOGGenerator,
                'nivel': 3
            },
            'resultadoog': {
                'generator_class': ResultadoOGGenerator,
                'nivel': 3
            },
            'resultadooe': {  
                'generator_class': ResultadoOEGenerator,
                'nivel': 4
            },
            'productooe': {   
                'generator_class': ProductoOEGenerator,
                'nivel': 4
            },
            'indicadorog': {
                'generator_class': IndicadorOGGenerator,
                'nivel': 3
            },
            'indicadorrog': {
                'generator_class': IndicadorROGGenerator,
                'nivel': 4
            },
            'indicadoroe': {  
                'generator_class': IndicadorOEGenerator,
                'nivel': 4
            },
            'indicadorroe': {  
                'generator_class': IndicadorROEGenerator,
                'nivel': 5
            },
            'productoroe': {   
                'generator_class': ProductoROEGenerator,
                'nivel': 5
            },
            'procesorog': {
                'generator_class': ProcesoGenerator,
                'nivel': 4
            },
            'procesoroe': {
                'generator_class': ProcesoGenerator,
                'nivel': 5
            },
            'procesopoe': {
                'generator_class': ProcesoGenerator,
                'nivel': 5
            }
        }
        self.actividad_generator = ActividadGenerator()
    
    def generar_reporte_encadenado(self, modelo, objeto_id, profundidad=2, incluir_detalles_actividades=True):
        """
        Genera reporte encadenado con actividades vinculadas a la jerarquía
        
        Args:
            modelo: Tipo de modelo (proyecto, objetivogeneral, etc.)
            objeto_id: ID del objeto
            profundidad: Niveles de jerarquía a incluir
            incluir_detalles_actividades: Si True, incluye tareas e informes de actividades
        """
        if modelo not in self.generators_registry:
            raise ValueError(f"Generador para '{modelo}' no registrado")
        
        # Obtener generador
        generator_class = self.generators_registry[modelo]['generator_class']
        generator = generator_class()
        
        # Generar reporte basado en el modelo
        if modelo == 'proyecto':
            proyecto = Proyecto.objects.get(id=objeto_id)
            
            # 1. SECCIÓN PRINCIPAL DEL PROYECTO
            generator._agregar_portada(proyecto)
            generator._agregar_informacion_basica(proyecto)
            generator._agregar_presupuesto_estado(proyecto)
            generator._agregar_relaciones(proyecto)
            
            # 2. JERARQUÍA ESTRATÉGICA CON ACTIVIDADES VINCULADAS
            self._agregar_jerarquia_estrategica_con_actividades(generator, proyecto, profundidad, incluir_detalles_actividades)
                        
        elif modelo == 'objetivogeneral':
            # Para objetivo general, generar su reporte individual
            objetivo_general = ObjetivoGeneralProyecto.objects.get(id=objeto_id)
            generator._agregar_portada(objetivo_general)
            generator._agregar_informacion_principal(objetivo_general)
            generator._agregar_analisis_riesgos(objetivo_general)
            
            # ENCADENAR elementos si hay profundidad
            if profundidad > 1:
                self._agregar_indicadores_og(generator, objetivo_general)
            
            if profundidad > 1:
                self._agregar_objetivos_especificos_og(generator, objetivo_general, profundidad)
            
            if profundidad > 1:
                self._agregar_resultados_og(generator, objetivo_general, profundidad)
            
            # Agregar actividades vinculadas específicamente a este objetivo general
            actividades_vinculadas = self._obtener_actividades_por_elemento_jerarquico('objetivogeneral', objetivo_general.id)
            if actividades_vinculadas:
                generator.document.add_heading('ACTIVIDADES VINCULADAS A ESTE OBJETIVO GENERAL', level=2)
                for actividad in actividades_vinculadas:
                    self._agregar_actividad_completa(generator, actividad, incluir_detalles_actividades)
        
        elif modelo == 'objetivoespecificoog':
            # Para objetivo específico del OG, usar su generador específico
            return generator.generar_reporte_objetivo_especifico_og(objeto_id, profundidad)
        
        elif modelo == 'resultadoog':
            # Para resultado OG, usar su generador específico
            resultado_og = ResultadoOG.objects.get(id=objeto_id)
            generator._agregar_portada(resultado_og)
            generator._agregar_informacion_principal(resultado_og)
            generator._agregar_analisis_riesgos(resultado_og)
            generator._agregar_vinculaciones(resultado_og)
            
            # ENCADENAR niveles inferiores si hay profundidad > 1
            if profundidad > 1:
                self._agregar_nivel_4_resultado_og(generator, resultado_og, profundidad)
            
            # Agregar actividades vinculadas específicamente a este resultado OG
            actividades_vinculadas = self._obtener_actividades_por_elemento_jerarquico('resultadoog', resultado_og.id)
            if actividades_vinculadas:
                generator.document.add_heading('ACTIVIDADES VINCULADAS A ESTE RESULTADO', level=2)
                for actividad in actividades_vinculadas:
                    self._agregar_actividad_completa(generator, actividad, incluir_detalles_actividades)
        
        elif modelo == 'indicadorog':
            # Para indicador OG, usar su generador específico
            return generator.generar_reporte_indicador_og(objeto_id)        
        elif modelo == 'indicadorrog':
            # Para indicador ROG, usar su generador específico
            return generator.generar_reporte_indicador_rog(objeto_id)
        elif modelo == 'indicadoroe':
            # Para indicador OE, usar su generador específico
            return generator.generar_reporte_indicador_oe(objeto_id)
        elif modelo == 'resultadooe':
            # Para resultado OE, usar su generador específico
            return generator.generar_reporte_resultado_oe(objeto_id)
        elif modelo == 'productooe':
            # Para producto OE, usar su generador específico
            return generator.generar_reporte_producto_oe(objeto_id)
        elif modelo == 'indicadorroe':
            # Para indicador ROE, usar su generador específico
            return generator.generar_reporte_indicador_roe(objeto_id)
        elif modelo == 'productoroe':
            # Para producto roe, usar su generador especifico
            return generator.generar_reporte_producto_roe(objeto_id)
        elif modelo in ['procesorog', 'procesoroe', 'procesopoe']:
             # Para procesos, usar el generador específico
            return generator.generar_reporte_proceso(objeto_id, modelo)
        
        return generator

    # ============================================================================
    # JERARQUÍA ESTRATÉGICA CON ACTIVIDADES VINCULADAS
    # ============================================================================

    def _agregar_jerarquia_estrategica_con_actividades(self, generator, proyecto, profundidad, incluir_detalles):
        """Agrega la jerarquía estratégica con actividades vinculadas a cada nivel"""
        
        generator.document.add_heading('JERARQUÍA ESTRATÉGICA DEL PROYECTO CON ACTIVIDADES', level=1)
        
        # Obtener objetivo general del proyecto
        try:
            objetivo_general = ObjetivoGeneralProyecto.objects.get(proyecto=proyecto)
            self._agregar_objetivo_general_con_actividades(generator, objetivo_general, profundidad, incluir_detalles)
        except ObjetivoGeneralProyecto.DoesNotExist:
            generator.document.add_paragraph('⚠️ No se ha definido objetivo general para este proyecto.')
        
        # Objetivos específicos directos del proyecto
        objetivos_especificos = ObjetivoEspecificoProyecto.objects.filter(proyecto=proyecto)
        if objetivos_especificos.exists():
            generator.document.add_heading('Objetivos Específicos Directos del Proyecto', level=2)
            for oe in objetivos_especificos:
                self._agregar_objetivo_especifico_directo_con_actividades(generator, oe, incluir_detalles)

    def _agregar_objetivo_general_con_actividades(self, generator, objetivo_general, profundidad, incluir_detalles):
        """Agrega objetivo general con sus actividades vinculadas"""
        
        generator.document.add_heading(f'🎯 OBJETIVO GENERAL: {objetivo_general.codigo}', level=2)
        generator.document.add_paragraph(objetivo_general.descripcion or 'Sin descripción')
        
        if objetivo_general.supuestos:
            p_sup = generator.document.add_paragraph()
            p_sup.add_run("Supuestos: ").bold = True
            p_sup.add_run(objetivo_general.supuestos)
            
        if objetivo_general.riesgos:
            p_risk = generator.document.add_paragraph()
            p_risk.add_run("Riesgos: ").bold = True
            p_risk.add_run(objetivo_general.riesgos)
        
        # ACTIVIDADES VINCULADAS AL OBJETIVO GENERAL
        actividades_og = self._obtener_actividades_por_elemento_jerarquico('objetivogeneral', objetivo_general.id)
        if actividades_og:
            generator.document.add_heading('📋 Actividades Vinculadas a este Objetivo General', level=3)
            for actividad in actividades_og:
                self._agregar_actividad_completa(generator, actividad, incluir_detalles)
        else:
            generator.document.add_paragraph('ℹ️ No hay actividades vinculadas directamente a este objetivo general.', style='Intense Quote')
        
        # ENCADENAR elementos si hay profundidad
        if profundidad > 1:
            self._agregar_indicadores_og_con_actividades(generator, objetivo_general, incluir_detalles)
        
        if profundidad > 1:
            self._agregar_objetivos_especificos_og_con_actividades(generator, objetivo_general, profundidad, incluir_detalles)
        
        if profundidad > 1:
            self._agregar_resultados_og_con_actividades(generator, objetivo_general, profundidad, incluir_detalles)

    def _agregar_objetivo_especifico_directo_con_actividades(self, generator, objetivo_especifico, incluir_detalles):
        """Agrega objetivo específico directo con sus actividades vinculadas"""
        generator.document.add_heading(f'🎯 {objetivo_especifico.codigo}', level=3)
        generator.document.add_paragraph(objetivo_especifico.descripcion or 'Sin descripción')
        
        if objetivo_especifico.supuestos:
            generator.document.add_paragraph(f"Supuestos: {objetivo_especifico.supuestos}")
        
        if objetivo_especifico.riesgos:
            generator.document.add_paragraph(f"Riesgos: {objetivo_especifico.riesgos}")
        
        # ACTIVIDADES VINCULADAS AL OBJETIVO ESPECÍFICO
        actividades_oe = self._obtener_actividades_por_elemento_jerarquico('objetivoespecifico', objetivo_especifico.id)
        if actividades_oe:
            generator.document.add_heading('📋 Actividades Vinculadas a este Objetivo Específico', level=4)
            for actividad in actividades_oe:
                self._agregar_actividad_completa(generator, actividad, incluir_detalles)
        else:
            generator.document.add_paragraph('ℹ️ No hay actividades vinculadas directamente a este objetivo específico.', style='Intense Quote')

    def _agregar_indicadores_og_con_actividades(self, generator, objetivo_general, incluir_detalles):
        """Agrega indicadores del objetivo general con actividades vinculadas"""
        indicadores_og = IndicadorObjetivoGeneral.objects.filter(objetivo_general=objetivo_general)
        
        if not indicadores_og.exists():
            return
        
        generator.document.add_heading('Indicadores del Objetivo General', level=3)
        
        for indicador in indicadores_og:
            generator.document.add_heading(f'📊 {indicador.codigo}', level=4)
            generator.document.add_paragraph(indicador.descripcion or 'Sin descripción')
            
            if indicador.baseline:
                generator.document.add_paragraph(f"Línea Base: {indicador.baseline}")
            if indicador.target_q1:
                generator.document.add_paragraph(f"Meta Q1: {indicador.target_q1}")
            
            # ACTIVIDADES VINCULADAS AL INDICADOR OG
            actividades_indicador = self._obtener_actividades_por_elemento_jerarquico('indicadorog', indicador.id)
            if actividades_indicador:
                generator.document.add_heading('📋 Actividades de Seguimiento', level=5)
                for actividad in actividades_indicador:
                    self._agregar_actividad_completa(generator, actividad, incluir_detalles)

    def _agregar_objetivos_especificos_og_con_actividades(self, generator, objetivo_general, profundidad, incluir_detalles):
        """Agrega objetivos específicos del OG con actividades vinculadas"""
        objetivos_especificos_og = ObjetivoEspecificoProyecto.objects.filter(objetivo_general=objetivo_general)
        
        if not objetivos_especificos_og.exists():
            return
        
        generator.document.add_heading('Objetivos Específicos Relacionados', level=3)
        
        for oe in objetivos_especificos_og:
            generator.document.add_heading(f'🎯 {oe.codigo}', level=4)
            generator.document.add_paragraph(oe.descripcion or 'Sin descripción')
            
            # ACTIVIDADES VINCULADAS AL OBJETIVO ESPECÍFICO OG
            actividades_oe = self._obtener_actividades_por_elemento_jerarquico('objetivoespecificoog', oe.id)
            if actividades_oe:
                generator.document.add_heading('📋 Actividades Vinculadas', level=5)
                for actividad in actividades_oe:
                    self._agregar_actividad_completa(generator, actividad, incluir_detalles)
            
            if profundidad > 2:
                # Agregar elementos del objetivo específico si hay más profundidad
                self._agregar_elementos_objetivo_especifico_con_actividades(generator, oe, incluir_detalles)

    def _agregar_resultados_og_con_actividades(self, generator, objetivo_general, profundidad, incluir_detalles):
        """Agrega resultados del OG con actividades vinculadas"""
        resultados_og = ResultadoOG.objects.filter(objetivo_general=objetivo_general)
        
        if not resultados_og.exists():
            return
        
        generator.document.add_heading('Resultados Esperados', level=3)
        
        for resultado in resultados_og:
            generator.document.add_heading(f'📈 {resultado.codigo}', level=4)
            generator.document.add_paragraph(resultado.descripcion or 'Sin descripción')
            
            # ACTIVIDADES VINCULADAS AL RESULTADO OG
            actividades_rog = self._obtener_actividades_por_elemento_jerarquico('resultadoog', resultado.id)
            if actividades_rog:
                generator.document.add_heading('📋 Actividades de Implementación', level=5)
                for actividad in actividades_rog:
                    self._agregar_actividad_completa(generator, actividad, incluir_detalles)

    def _agregar_elementos_objetivo_especifico_con_actividades(self, generator, objetivo_especifico, incluir_detalles):
        """Agrega elementos de un objetivo específico con actividades vinculadas"""
        
        # Indicadores del OE
        indicadores_oe = objetivo_especifico.indicador_oe.all()
        if indicadores_oe.exists():
            generator.document.add_heading('Indicadores', level=5)
            for indicador in indicadores_oe:
                generator.document.add_paragraph(f'• {indicador.codigo}: {indicador.descripcion[:100]}...' if indicador.descripcion else f'• {indicador.codigo}')
                
                # ACTIVIDADES VINCULADAS AL INDICADOR OE
                actividades_indicador_oe = self._obtener_actividades_por_elemento_jerarquico('indicadoroe', indicador.id)
                if actividades_indicador_oe:
                    generator.document.add_heading('📋 Actividades de Medición', level=6)
                    for actividad in actividades_indicador_oe:
                        self._agregar_actividad_completa(generator, actividad, incluir_detalles)

        # Resultados del OE
        resultados_oe = objetivo_especifico.resultados_oe.all()
        if resultados_oe.exists():
            generator.document.add_heading('Resultados', level=5)
            for resultado in resultados_oe:
                generator.document.add_paragraph(f'• {resultado.codigo}: {resultado.descripcion[:100]}...' if resultado.descripcion else f'• {resultado.codigo}')
                
                # ACTIVIDADES VINCULADAS AL RESULTADO OE
                actividades_roe = self._obtener_actividades_por_elemento_jerarquico('resultadooe', resultado.id)
                if actividades_roe:
                    generator.document.add_heading('📋 Actividades de Resultado', level=6)
                    for actividad in actividades_roe:
                        self._agregar_actividad_completa(generator, actividad, incluir_detalles)

        # Productos del OE
        productos_oe = objetivo_especifico.productos_oe.all()
        if productos_oe.exists():
            generator.document.add_heading('Productos', level=5)
            for producto in productos_oe:
                generator.document.add_paragraph(f'• {producto.codigo}: {producto.descripcion[:100]}...' if producto.descripcion else f'• {producto.codigo}')
                
                # ACTIVIDADES VINCULADAS AL PRODUCTO OE
                actividades_producto = self._obtener_actividades_por_elemento_jerarquico('productooe', producto.id)
                if actividades_producto:
                    generator.document.add_heading('📋 Actividades de Producción', level=6)
                    for actividad in actividades_producto:
                        self._agregar_actividad_completa(generator, actividad, incluir_detalles)

    # ============================================================================
    # MÉTODOS PARA OBTENER ACTIVIDADES VINCULADAS
    # ============================================================================

    def _obtener_actividades_por_elemento_jerarquico(self, tipo_elemento, elemento_id):
        """
        Obtiene actividades vinculadas a un elemento específico de la jerarquía
        
        Args:
            tipo_elemento: Tipo de elemento (objetivogeneral, resultadoog, etc.)
            elemento_id: ID del elemento específico
        """
        actividades_vinculadas = []
        
        # Obtener todas las actividades del proyecto relacionado
        if tipo_elemento == 'objetivogeneral':
            objetivo_general = ObjetivoGeneralProyecto.objects.get(id=elemento_id)
            actividades_proyecto = Actividad.objects.filter(proyecto=objetivo_general.proyecto)
        else:
            # Para otros elementos, necesitamos encontrar el proyecto padre
            proyecto = self._obtener_proyecto_por_elemento(tipo_elemento, elemento_id)
            if proyecto:
                actividades_proyecto = Actividad.objects.filter(proyecto=proyecto)
            else:
                return []
        
        # Filtrar actividades que referencian este elemento específico
        for actividad in actividades_proyecto:
            if self._actividad_vincula_elemento(actividad, tipo_elemento, elemento_id):
                actividades_vinculadas.append(actividad)
        
        return actividades_vinculadas

    def _obtener_proyecto_por_elemento(self, tipo_elemento, elemento_id):
        """Obtiene el proyecto padre de cualquier elemento de la jerarquía"""
        try:
            if tipo_elemento == 'objetivogeneral':
                return ObjetivoGeneralProyecto.objects.get(id=elemento_id).proyecto
            elif tipo_elemento == 'objetivoespecificoog':
                return ObjetivoEspecificoProyecto.objects.get(id=elemento_id).proyecto
            elif tipo_elemento == 'resultadoog':
                return ResultadoOG.objects.get(id=elemento_id).objetivo_general.proyecto
            elif tipo_elemento == 'indicadorog':
                return IndicadorObjetivoGeneral.objects.get(id=elemento_id).objetivo_general.proyecto
            elif tipo_elemento == 'indicadorrog':
                return IndicadorResultadoObjGral.objects.get(id=elemento_id).resultado_og.objetivo_general.proyecto
            elif tipo_elemento == 'objetivoespecifico':
                return ObjetivoEspecificoProyecto.objects.get(id=elemento_id).proyecto
            elif tipo_elemento == 'indicadoroe':
                return IndicadorObjetivoEspecifico.objects.get(id=elemento_id).objetivo_especifico.proyecto
            elif tipo_elemento == 'resultadooe':
                return ResultadoOE.objects.get(id=elemento_id).objetivo_especifico.proyecto
            elif tipo_elemento == 'productooe':
                return ProductoOE.objects.get(id=elemento_id).objetivo_especifico.proyecto
            elif tipo_elemento == 'indicadorroe':
                return IndicadorResultadoObjEspecifico.objects.get(id=elemento_id).resultado_oe.objetivo_especifico.proyecto
            elif tipo_elemento == 'productoroe':
                return ProductoResultadoOE.objects.get(id=elemento_id).resultado_oe.objetivo_especifico.proyecto
            elif tipo_elemento in ['procesorog', 'procesoroe', 'procesopoe']:
                proceso = Proceso.objects.get(id=elemento_id)
                # Aquí necesitarías la lógica para obtener el proyecto desde el proceso
                return None
        except Exception as e:
            self.logger.error(f"Error obteniendo proyecto para {tipo_elemento} {elemento_id}: {str(e)}")
            return None
        
        return None

    def _actividad_vincula_elemento(self, actividad, tipo_elemento, elemento_id):
        """
        Verifica si una actividad vincula un elemento específico mediante estructuraProcedencia
        """
        if not actividad.estructuraProcedencia:
            return False
        
        estructura = actividad.estructuraProcedencia
        datos_procedencia = estructura.get('datosProcedencia', {})
        
        if tipo_elemento not in datos_procedencia:
            return False
        
        elemento_actividad = datos_procedencia[tipo_elemento]
        
        # Manejar diferentes estructuras de datos
        if isinstance(elemento_actividad, dict):
            data = elemento_actividad.get('data', {})
            return data.get('id') == elemento_id
        elif isinstance(elemento_actividad, list):
            for elem in elemento_actividad:
                if isinstance(elem, dict):
                    data = elem.get('data', {})
                    if data.get('id') == elemento_id:
                        return True
        elif isinstance(elemento_actividad, str):
            # Si es string, podría ser el ID directamente
            return str(elemento_actividad) == str(elemento_id)
        
        return False

    # ============================================================================
    # SECCIÓN COMPLETA DE ACTIVIDADES (métodos existentes)
    # ============================================================================

    def _agregar_actividad_completa(self, generator, actividad, incluir_detalles=True):
        """Agrega una actividad completa con todas sus tareas e informes"""
        
        generator.document.add_heading(f'📋 ACTIVIDAD: {actividad.codigo} - {actividad.nombreCorto}', level=3)
        
        # Información básica de la actividad
        self._agregar_info_basica_actividad(generator, actividad)
        
        # Vinculaciones de la actividad
        if actividad.estructuraProcedencia:
            self._agregar_vinculaciones_actividad(generator, actividad)
        
        # Tareas/Subactividades si se solicitan detalles
        if incluir_detalles:
            self._agregar_tareas_actividad(generator, actividad)
        
        # Informes de la actividad si se solicitan detalles
        if incluir_detalles:
            self._agregar_informes_actividad(generator, actividad)
        
        generator.document.add_paragraph('=' * 80)
        generator.document.add_paragraph()

    def _agregar_info_basica_actividad(self, generator, actividad):
        """Agrega información básica de la actividad"""
        
        tabla_info = generator.document.add_table(rows=8, cols=2)
        tabla_info.style = 'Light Grid Accent 1'
        
        datos_actividad = [
            ('Código', actividad.codigo or 'No definido'),
            ('Nombre Corto', actividad.nombreCorto or 'Sin nombre'),
            ('Estado', actividad.get_estado_display()),
            ('Tipo', actividad.tipo.tipo_actividad if actividad.tipo else 'No definido'),
            ('Presupuesto', self._formatear_moneda(actividad.presupuesto)),
            ('Grado Ejecución', actividad.gradoEjecucion or 'No definido'),
            ('Fecha Inicio', self._formatear_fecha(actividad.fecha_inicio)),
            ('Fecha Cierre', self._formatear_fecha(actividad.fecha_cierre))
        ]
        
        for i, (campo, valor) in enumerate(datos_actividad):
            tabla_info.cell(i, 0).text = campo
            tabla_info.cell(i, 1).text = str(valor)
            tabla_info.cell(i, 0).paragraphs[0].runs[0].bold = True
        
        generator.document.add_paragraph()
        
        # Descripción
        if actividad.descripcion:
            p_desc = generator.document.add_paragraph()
            p_desc.add_run('Descripción: ').bold = True
            p_desc.add_run(actividad.descripcion)
            generator.document.add_paragraph()
        
        # Objetivo de la actividad
        if actividad.objetivo_de_actividad:
            p_obj = generator.document.add_paragraph()
            p_obj.add_run('Objetivo: ').bold = True
            p_obj.add_run(actividad.objetivo_de_actividad)
            generator.document.add_paragraph()

    def _agregar_tareas_actividad(self, generator, actividad):
        """Agrega las tareas/subactividades de una actividad"""
        
        tareas = TareaActividad.objects.filter(actividad=actividad).order_by('fecha_creacion')
        if not tareas.exists():
            return
        
        generator.document.add_heading('📝 Tareas/Subactividades', level=4)
        
        for i, tarea in enumerate(tareas, 1):
            generator.document.add_heading(f'Tarea {i}: {tarea.codigo or "Sin código"}', level=5)
            
            # Información de la tarea
            tabla_tarea = generator.document.add_table(rows=6, cols=2)
            tabla_tarea.style = 'Light Grid Accent 2'
            
            datos_tarea = [
                ('Código', tarea.codigo or 'No definido'),
                ('Título', tarea.titulo or 'Sin título'),
                ('Estado', tarea.get_estado_display()),
                ('Fecha Creación', self._formatear_fecha(tarea.fecha_creacion)),
                ('Fecha Ejecución', self._formatear_fecha(tarea.fecha_ejecucion)),
                ('Fecha Límite', self._formatear_fecha(tarea.fecha_limite))
            ]
            
            for j, (campo, valor) in enumerate(datos_tarea):
                tabla_tarea.cell(j, 0).text = campo
                tabla_tarea.cell(j, 1).text = str(valor)
                tabla_tarea.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            
            # Descripción de la tarea
            if tarea.descripcion:
                p_desc_tarea = generator.document.add_paragraph()
                p_desc_tarea.add_run('Descripción: ').bold = True
                p_desc_tarea.add_run(tarea.descripcion)
                generator.document.add_paragraph()
            
            # Informes de la tarea
            self._agregar_informes_tarea(generator, tarea)
            
            generator.document.add_paragraph('―' * 50)
            generator.document.add_paragraph()

    def _agregar_informes_actividad(self, generator, actividad):
        """Agrega los informes de una actividad"""
        
        informes = InfActividad.objects.filter(actividad=actividad).order_by('fecha_ejecucion')
        if not informes.exists():
            return
        
        generator.document.add_heading('📊 Informes de Actividad', level=4)
        
        for i, informe in enumerate(informes, 1):
            generator.document.add_heading(f'Informe {i}: {informe.numeroInforme or "Sin número"}', level=5)
            
            # Información del informe
            tabla_informe = generator.document.add_table(rows=5, cols=2)
            tabla_informe.style = 'Light Grid Accent 3'
            
            datos_informe = [
                ('Número de Informe', informe.numeroInforme or 'No definido'),
                ('Fecha de Ejecución', self._formatear_fecha(informe.fecha_ejecucion)),
                ('Tipo de Actividad', informe.tipo_actividad or 'No especificado'),
                ('Presupuesto Planificado', self._formatear_moneda(informe.presupuesto_planificado)),
                ('Presupuesto Ejecutado', self._formatear_moneda(informe.presupuesto_ejecutado)),
            ]
            
            for j, (campo, valor) in enumerate(datos_informe):
                tabla_informe.cell(j, 0).text = campo
                tabla_informe.cell(j, 1).text = str(valor)
                tabla_informe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            
            # Información adicional del informe
            if informe.objetivo_actividad:
                p_obj = generator.document.add_paragraph()
                p_obj.add_run('Objetivo: ').bold = True
                p_obj.add_run(informe.objetivo_actividad)
            
            if informe.informe_objetivo_actividad:
                p_inf_obj = generator.document.add_paragraph()
                p_inf_obj.add_run('Informe del Objetivo: ').bold = True
                p_inf_obj.add_run(informe.informe_objetivo_actividad)
            
            generator.document.add_paragraph('―' * 40)
            generator.document.add_paragraph()

    def _agregar_informes_tarea(self, generator, tarea):
        """Agrega los informes de una tarea/subactividad"""
        
        informes = InfTarea.objects.filter(tarea=tarea).order_by('fecha_ejecucion')
        if not informes.exists():
            return
        
        generator.document.add_heading('📋 Informes de la Tarea', level=6)
        
        for i, informe in enumerate(informes, 1):
            generator.document.add_heading(f'Informe Tarea {i}: {informe.numeroInforme or "Sin número"}', level=7)
            
            # Información del informe de tarea
            tabla_informe = generator.document.add_table(rows=5, cols=2)
            tabla_informe.style = 'Table Grid'
            
            datos_informe = [
                ('Número de Informe', informe.numeroInforme or 'No definido'),
                ('Fecha de Ejecución', self._formatear_fecha(informe.fecha_ejecucion)),
                ('Presupuesto Planificado', self._formatear_moneda(informe.presupuesto_planificado)),
                ('Presupuesto Ejecutado', self._formatear_moneda(informe.presupuesto_ejecutado)),
            ]
            
            for j, (campo, valor) in enumerate(datos_informe):
                tabla_informe.cell(j, 0).text = campo
                tabla_informe.cell(j, 1).text = str(valor)
                tabla_informe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            
            # Información adicional
            if informe.objetivo_tarea:
                p_obj = generator.document.add_paragraph()
                p_obj.add_run('Objetivo: ').bold = True
                p_obj.add_run(informe.objetivo_tarea)
            
            generator.document.add_paragraph('―' * 30)
            generator.document.add_paragraph()

    def _agregar_vinculaciones_actividad(self, generator, actividad):
        """Muestra las vinculaciones de la actividad mediante estructuraProcedencia"""
        
        estructura = actividad.estructuraProcedencia
        if not estructura:
            return
        
        generator.document.add_paragraph('🔗 Vinculaciones:')
        
        datos_procedencia = estructura.get('datosProcedencia', {})
        vinculaciones = []
        
        mapeo_tipos = {
            'objetivogeneral': 'Objetivo General',
            'objetivoespecificoog': 'Objetivo Específico (OG)',
            'objetivoespecifico': 'Objetivo Específico',
            'indicadorog': 'Indicador OG',
            'indicadoroe': 'Indicador OE',
            'resultadoog': 'Resultado OG',
            'resultadooe': 'Resultado OE',
            'productooe': 'Producto OE',
            'productoroe': 'Producto ROE',
            'indicadorrog': 'Indicador ROG',
            'indicadorroe': 'Indicador ROE',
            'procesorog': 'Proceso ROG',
            'procesoroe': 'Proceso ROE',
            'procesopoe': 'Proceso POE'
        }
        
        for tipo, elemento in datos_procedencia.items():
            if elemento:
                nombre_tipo = mapeo_tipos.get(tipo, tipo)
                if isinstance(elemento, dict):
                    codigo = elemento.get('data', {}).get('codigo', 'No definido')
                    vinculaciones.append(f"• {nombre_tipo}: {codigo}")
                elif isinstance(elemento, list):
                    for elem in elemento:
                        if isinstance(elem, dict):
                            codigo = elem.get('data', {}).get('codigo', 'No definido')
                            vinculaciones.append(f"• {nombre_tipo}: {codigo}")
        
        for vinculacion in vinculaciones:
            generator.document.add_paragraph(vinculacion, style='List Bullet')
        
        generator.document.add_paragraph()

    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================

    def _clasificar_actividades_por_tipo(self, actividades):
        """Clasifica actividades según los tipos en estructuraProcedencia"""
        actividades_por_tipo = {}
        
        for actividad in actividades:
            estructura = actividad.estructuraProcedencia
            if isinstance(estructura, dict):
                datos_procedencia = estructura.get('datosProcedencia', {})
                for tipo_elemento in datos_procedencia.keys():
                    if tipo_elemento not in actividades_por_tipo:
                        actividades_por_tipo[tipo_elemento] = []
                    if actividad not in actividades_por_tipo[tipo_elemento]:
                        actividades_por_tipo[tipo_elemento].append(actividad)
        
        return actividades_por_tipo

    def _obtener_nombre_seccion(self, tipo_elemento):
        """Convierte tipo de elemento a nombre legible para sección"""
        mapeo_nombres = {
            'objetivogeneral': 'Objetivo General',
            'objetivoespecificoog': 'Objetivo Específico (OG)',
            'objetivoespecifico': 'Objetivo Específico',
            'indicadorog': 'Indicador OG',
            'indicadoroe': 'Indicador OE',
            'resultadoog': 'Resultado OG',
            'resultadooe': 'Resultado OE',
            'productooe': 'Producto OE',
            'productoroe': 'Producto ROE',
            'indicadorrog': 'Indicador ROG',
            'indicadorroe': 'Indicador ROE',
            'procesorog': 'Proceso ROG',
            'procesoroe': 'Proceso ROE',
            'procesopoe': 'Proceso POE'
        }
        return mapeo_nombres.get(tipo_elemento, tipo_elemento.title())

    def _formatear_moneda(self, valor):
        """Formatea valores monetarios"""
        if valor is None:
            return "No definido"
        try:
            return f"${float(valor):,.2f}"
        except (TypeError, ValueError):
            return "Formato inválido"

    def _formatear_fecha(self, fecha):
        """Formatea fechas"""
        if not fecha:
            return "No definida"
        return fecha.strftime("%d/%m/%Y")

    # ============================================================================
    # MÉTODOS EXISTENTES DEL CHAIN COMPOSER (para compatibilidad)
    # ============================================================================

    def _agregar_indicadores_og(self, generator, objetivo_general):
        """Agrega indicadores relacionados al objetivo general"""
        indicadores_og = IndicadorObjetivoGeneral.objects.filter(objetivo_general=objetivo_general)
        
        if not indicadores_og.exists():
            generator.document.add_heading('Indicadores del Objetivo General', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido indicadores para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('INDICADORES DEL OBJETIVO GENERAL', level=3)
        generator.document.add_paragraph("Indicadores para medir el avance del objetivo general:")
        
        for i, indicador in enumerate(indicadores_og, 1):
            generator.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=4)
            
            tabla_indicador = generator.document.add_table(rows=8, cols=2)
            tabla_indicador.style = 'Light Grid Accent 1'
            
            datos_indicador = [
                ('Código', indicador.codigo or 'No definido'),
                ('Descripción', indicador.descripcion or 'No disponible'),
                ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
                ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
                ('Línea Base', indicador.baseline or 'No definida'),
                ('Meta Q1', indicador.target_q1 or 'No definida'),
                ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
                ('Responsable', indicador.responsable or 'No asignado')
            ]
            
            for j, (campo, valor) in enumerate(datos_indicador):
                tabla_indicador.cell(j, 0).text = campo
                tabla_indicador.cell(j, 1).text = str(valor)
                tabla_indicador.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            generator.document.add_paragraph("―" * 60)
            generator.document.add_paragraph()

    def _agregar_objetivos_especificos_og(self, generator, objetivo_general, profundidad):
        """Agrega objetivos específicos relacionados al objetivo general"""
        objetivos_especificos_og = ObjetivoEspecificoProyecto.objects.filter(objetivo_general=objetivo_general)
        
        if not objetivos_especificos_og.exists():
            generator.document.add_heading('Objetivos Específicos Relacionados', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido objetivos específicos para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('OBJETIVOS ESPECÍFICOS RELACIONADOS', level=3)
        generator.document.add_paragraph("Objetivos operativos que contribuyen al logro del objetivo general:")
        
        for i, oe in enumerate(objetivos_especificos_og, 1):
            generator.document.add_heading(f'Objetivo Específico {i}: {oe.codigo}', level=4)
            
            tabla_oe = generator.document.add_table(rows=4, cols=2)
            tabla_oe.style = 'Light Grid Accent 2'
            
            datos_oe = [
                ('Código', oe.codigo or 'No definido'),
                ('Descripción', oe.descripcion or 'No disponible'),
                ('Supuestos', oe.supuestos or 'No definidos'),
                ('Riesgos', oe.riesgos or 'No identificados')
            ]
            
            for j, (campo, valor) in enumerate(datos_oe):
                tabla_oe.cell(j, 0).text = campo
                tabla_oe.cell(j, 1).text = str(valor)
                tabla_oe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            generator.document.add_paragraph("―" * 60)
            generator.document.add_paragraph()

    def _agregar_resultados_og(self, generator, objetivo_general, profundidad):
        """Agrega resultados relacionados al objetivo general"""
        resultados_og = ResultadoOG.objects.filter(objetivo_general=objetivo_general)
        
        if not resultados_og.exists():
            generator.document.add_heading('Resultados Relacionados', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido resultados para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('RESULTADOS ESPERADOS', level=3)
        generator.document.add_paragraph("Resultados estratégicos que se esperan del objetivo general:")
        
        for i, resultado in enumerate(resultados_og, 1):
            generator.document.add_heading(f'Resultado {i}: {resultado.codigo}', level=4)
            
            tabla_resultado = generator.document.add_table(rows=4, cols=2)
            tabla_resultado.style = 'Light Grid Accent 3'
            
            datos_resultado = [
                ('Código', resultado.codigo or 'No definido'),
                ('Descripción', resultado.descripcion or 'No disponible'),
                ('Supuestos', resultado.supuestos or 'No definidos'),
                ('Riesgos', resultado.riesgos or 'No identificados')
            ]
            
            for j, (campo, valor) in enumerate(datos_resultado):
                tabla_resultado.cell(j, 0).text = campo
                tabla_resultado.cell(j, 1).text = str(valor)
                tabla_resultado.cell(j, 0).paragraphs[0].runs[0].bold = True
            
            generator.document.add_paragraph()
            generator.document.add_paragraph("―" * 60)
            generator.document.add_paragraph()

    def _agregar_nivel_4_resultado_og(self, generator, resultado_og, profundidad):
        """Agrega nivel 4: Indicadores y Procesos del Resultado OG"""
        # Implementación básica para mantener compatibilidad
        generator.document.add_heading('Elementos del Resultado', level=5)
        generator.document.add_paragraph("Indicadores y procesos relacionados con este resultado.")
        
        # Aquí se podrían agregar más detalles específicos si es necesario

    # ============================================================================
    # MÉTODO PRINCIPAL DE DESCARGA
    # ============================================================================

    def generar_y_descargar(self, modelo, objeto_id, profundidad=2, incluir_detalles_actividades=True):
        """Genera y descarga el reporte encadenado"""
        try:
            modelos_directos = [
                'objetivoespecificoog', 'resultadoog', 'resultadooe', 'productooe',
                'indicadorog', 'indicadorrog', 'indicadoroe', 'indicadorroe', 'productoroe',
                'procesorog', 'procesoroe', 'procesopoe'
            ]
            
            if modelo in modelos_directos:
                generator = self.generators_registry[modelo]['generator_class']()
                if modelo == 'objetivoespecificoog':
                    buffer = generator.generar_reporte_objetivo_especifico_og(objeto_id, profundidad)
                elif modelo == 'resultadoog':
                    buffer = generator.generar_reporte_resultado_og(objeto_id)
                elif modelo == 'resultadooe':
                    buffer = generator.generar_reporte_resultado_oe(objeto_id)
                elif modelo == 'productooe':
                    buffer = generator.generar_reporte_producto_oe(objeto_id)
                elif modelo == 'indicadorog':
                    buffer = generator.generar_reporte_indicador_og(objeto_id)
                elif modelo == 'indicadorrog':
                    buffer = generator.generar_reporte_indicador_rog(objeto_id)    
                elif modelo == 'indicadoroe':
                    buffer = generator.generar_reporte_indicador_oe(objeto_id)
                elif modelo == 'indicadorroe':
                    buffer = generator.generar_reporte_indicador_roe(objeto_id)
                elif modelo == 'productoroe':
                    buffer = generator.generar_reporte_producto_roe(objeto_id)
                elif modelo in ['procesorog', 'procesoroe', 'procesopoe']:
                    buffer = generator.generar_reporte_proceso(objeto_id, modelo)
            else:
                # Para proyecto y objetivo general, usar el encadenamiento mejorado
                generator = self.generar_reporte_encadenado(
                    modelo, objeto_id, profundidad, incluir_detalles_actividades
                )
                buffer = generator._guardar_documento()
            
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_encadenado_{modelo}_{objeto_id}.docx"'
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {str(e)}")
            raise ValueError(f"Error generando reporte: {str(e)}")




# from django.http import HttpResponse
# import os
# import django

# # Configurar Django explícitamente
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
# django.setup()

# from spme_estructuracion_proyecto.models import (
#     Proyecto, 
#     ObjetivoGeneralProyecto, 
#     ObjetivoEspecificoProyecto,
#     ResultadoOG,
#     ResultadoOE,
#     IndicadorObjetivoGeneral,
#     IndicadorResultadoObjGral,
#     IndicadorObjetivoEspecifico,
#     ProductoOE,
#     Proceso,
#     IndicadorResultadoObjEspecifico,
#     ProductoResultadoOE,
# )
# from ..generators.proyecto_generator import ProyectoGenerator
# from ..generators.objetivo_general_generator import ObjetivoGeneralGenerator
# from ..generators.objetivo_especifico_og_generator import ObjetivoEspecificoOGGenerator
# from ..generators.resultado_og_generator import ResultadoOGGenerator
# from ..generators.indicador_og_generator import IndicadorOGGenerator
# from ..generators.indicador_rog_generator import IndicadorROGGenerator
# from ..generators.indicador_oe_generator import IndicadorOEGenerator
# from ..generators.resultado_oe_generator import ResultadoOEGenerator
# from ..generators.producto_oe_generator import ProductoOEGenerator 
# from ..generators.indicador_roe_generator import IndicadorROEGenerator
# # ✅ AGREGAR ESTOS GENERADORES
# from ..generators.producto_roe_generator import ProductoROEGenerator
# from ..generators.proceso_generator import ProcesoGenerator


# class ChainComposer:
#     """
#     Orquestador principal para encadenamiento de reportes
#     """
    
#     def __init__(self):
#         self.generators_registry = {
#             'proyecto': {
#                 'generator_class': ProyectoGenerator,
#                 'nivel': 1
#             },
#             'objetivogeneral': {
#                 'generator_class': ObjetivoGeneralGenerator, 
#                 'nivel': 2
#             },
#             'objetivoespecificoog': {
#                 'generator_class': ObjetivoEspecificoOGGenerator,
#                 'nivel': 3
#             },
#             'resultadoog': {
#                 'generator_class': ResultadoOGGenerator,
#                 'nivel': 3
#             },
#             'resultadooe': {  
#                 'generator_class': ResultadoOEGenerator,
#                 'nivel': 4
#             },
#             'productooe': {   
#                 'generator_class': ProductoOEGenerator,
#                 'nivel': 4
#             },
#             'indicadorog': {
#                 'generator_class': IndicadorOGGenerator,
#                 'nivel': 3
#             },
#             'indicadorrog': {
#                 'generator_class': IndicadorROGGenerator,
#                 'nivel': 4
#             },
#             'indicadoroe': {  
#                 'generator_class': IndicadorOEGenerator,
#                 'nivel': 4
#             },
#             'indicadorroe': {  
#                 'generator_class': IndicadorROEGenerator,
#                 'nivel': 5
#             },
#             'productoroe': {   
#                 'generator_class': ProductoROEGenerator,
#                 'nivel': 5
#             },
#             'procesorog': {
#                 'generator_class': ProcesoGenerator,
#                 'nivel': 4
#             },
#             'procesoroe': {
#                 'generator_class': ProcesoGenerator,
#                 'nivel': 5
#             },
#             'procesopoe': {
#                 'generator_class': ProcesoGenerator,
#                 'nivel': 5
#             }
#         }
    
#     def generar_reporte_encadenado(self, modelo, objeto_id, profundidad=2):
#         """
#         Genera reporte encadenado
#         """
#         if modelo not in self.generators_registry:
#             raise ValueError(f"Generador para '{modelo}' no registrado")
        
#         # Obtener generador
#         generator_class = self.generators_registry[modelo]['generator_class']
#         generator = generator_class()
        
#         # Generar reporte basado en el modelo
#         if modelo == 'proyecto':
#             proyecto = Proyecto.objects.get(id=objeto_id)
            
#             # Generar secciones principales del proyecto
#             generator._agregar_portada(proyecto)
#             generator._agregar_informacion_basica(proyecto)
#             generator._agregar_presupuesto_estado(proyecto)
#             generator._agregar_relaciones(proyecto)
            
#             # ENCADENAR objetivos generales si hay profundidad > 1
#             if profundidad > 1:
#                 objetivos_generales = ObjetivoGeneralProyecto.objects.filter(proyecto=proyecto)
#                 if objetivos_generales.exists():
#                     generator.document.add_heading('OBJETIVOS GENERALES ENCADENADOS', level=1)
                    
#                     for og in objetivos_generales:
#                         # Agregar información del objetivo general al documento
#                         generator.document.add_heading(f"Objetivo General: {og.codigo}", level=2)
                        
#                         p_desc = generator.document.add_paragraph()
#                         p_desc.add_run("Descripción: ").bold = True
#                         p_desc.add_run(og.descripcion or "No disponible")
                        
#                         if og.supuestos:
#                             p_sup = generator.document.add_paragraph()
#                             p_sup.add_run("Supuestos: ").bold = True
#                             p_sup.add_run(og.supuestos)
                            
#                         if og.riesgos:
#                             p_risk = generator.document.add_paragraph()
#                             p_risk.add_run("Riesgos: ").bold = True
#                             p_risk.add_run(og.riesgos)
                        
#                         # ENCADENAR indicadores del objetivo general si hay profundidad > 2
#                         if profundidad > 2:
#                             self._agregar_indicadores_og(generator, og)
                        
#                         # ENCADENAR objetivos específicos del objetivo general si hay profundidad > 2
#                         if profundidad > 2:
#                             self._agregar_objetivos_especificos_og(generator, og, profundidad)
                        
#                         # ENCADENAR resultados del objetivo general si hay profundidad > 2
#                         if profundidad > 2:
#                             self._agregar_resultados_og(generator, og, profundidad)
                        
#                         generator.document.add_paragraph()  # Espacio entre objetivos
                        
#         elif modelo == 'objetivogeneral':
#             # Para objetivo general, generar su reporte individual
#             objetivo_general = ObjetivoGeneralProyecto.objects.get(id=objeto_id)
#             generator._agregar_portada(objetivo_general)
#             generator._agregar_informacion_principal(objetivo_general)
#             generator._agregar_analisis_riesgos(objetivo_general)
            
#             # ENCADENAR indicadores del objetivo general si hay profundidad > 1
#             if profundidad > 1:
#                 self._agregar_indicadores_og(generator, objetivo_general)
            
#             # ENCADENAR objetivos específicos del objetivo general si hay profundidad > 1
#             if profundidad > 1:
#                 self._agregar_objetivos_especificos_og(generator, objetivo_general, profundidad)
            
#             # ENCADENAR resultados del objetivo general si hay profundidad > 1
#             if profundidad > 1:
#                 self._agregar_resultados_og(generator, objetivo_general, profundidad)
        
#         elif modelo == 'objetivoespecificoog':
#             # Para objetivo específico del OG, usar su generador específico
#             #return generator.generar_reporte_objetivo_especifico_og(objeto_id)
#             return generator.generar_reporte_objetivo_especifico_og(objeto_id, profundidad)
        
#         elif modelo == 'resultadoog':
#             # Para resultado OG, usar su generador específico
#             resultado_og = ResultadoOG.objects.get(id=objeto_id)
#             generator._agregar_portada(resultado_og)
#             generator._agregar_informacion_principal(resultado_og)
#             generator._agregar_analisis_riesgos(resultado_og)
#             generator._agregar_vinculaciones(resultado_og)
            
#             # ENCADENAR niveles inferiores si hay profundidad > 1
#             if profundidad > 1:
#                 self._agregar_nivel_4_resultado_og(generator, resultado_og, profundidad)
        
#         elif modelo == 'indicadorog':
#             # Para indicador OG, usar su generador específico
#             return generator.generar_reporte_indicador_og(objeto_id)        
#         elif modelo == 'indicadorrog':
#             # Para indicador ROG, usar su generador específico
#             return generator.generar_reporte_indicador_rog(objeto_id)
#         elif modelo == 'indicadoroe':
#             # Para indicador OE, usar su generador específico
#             return generator.generar_reporte_indicador_oe(objeto_id)
#         elif modelo == 'resultadooe':
#             # Para resultado OE, usar su generador específico
#             return generator.generar_reporte_resultado_oe(objeto_id)
#         elif modelo == 'productooe':
#             # Para producto OE, usar su generador específico
#             return generator.generar_reporte_producto_oe(objeto_id)
#         elif modelo == 'indicadorroe':
#             # Para indicador ROE, usar su generador específico
#             return generator.generar_reporte_indicador_roe(objeto_id)
#         elif modelo == 'productoroe':
#             # Para producto roe, usar su generador especifico
#             return generator.generar_reporte_producto_roe(objeto_id)
#         elif modelo in ['procesorog', 'procesoroe', 'procesopoe']:
#              # Para procesos, usar el generador específico
#             return generator.generar_reporte_proceso(objeto_id, modelo)
#         return generator

#     def _agregar_indicadores_og(self, generator, objetivo_general):
#         """Agrega indicadores relacionados al objetivo general"""
#         indicadores_og = IndicadorObjetivoGeneral.objects.filter(
#             objetivo_general=objetivo_general
#         )
        
#         if not indicadores_og.exists():
#             generator.document.add_heading('Indicadores del Objetivo General', level=3)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido indicadores para este objetivo general.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('INDICADORES DEL OBJETIVO GENERAL', level=3)
#         generator.document.add_paragraph("Indicadores para medir el avance del objetivo general:")
        
#         for i, indicador in enumerate(indicadores_og, 1):
#             # Información del indicador
#             generator.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=4)
            
#             # Tabla de información principal
#             tabla_indicador = generator.document.add_table(rows=8, cols=2)
#             tabla_indicador.style = 'Light Grid Accent 1'
            
#             datos_indicador = [
#                 ('Código', indicador.codigo or 'No definido'),
#                 ('Descripción', indicador.descripcion or 'No disponible'),
#                 ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
#                 ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
#                 ('Línea Base', indicador.baseline or 'No definida'),
#                 ('Meta Q1', indicador.target_q1 or 'No definida'),
#                 ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
#                 ('Responsable', indicador.responsable or 'No asignado')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_indicador):
#                 tabla_indicador.cell(j, 0).text = campo
#                 tabla_indicador.cell(j, 1).text = str(valor)
#                 tabla_indicador.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
#             generator.document.add_paragraph("―" * 60)
#             generator.document.add_paragraph()

#     def _agregar_objetivos_especificos_og(self, generator, objetivo_general, profundidad):
#         """Agrega objetivos específicos relacionados al objetivo general con niveles inferiores"""
#         objetivos_especificos_og = ObjetivoEspecificoProyecto.objects.filter(
#             objetivo_general=objetivo_general
#         ).prefetch_related(
#             'indicador_oe',
#             'resultados_oe',    
#             'productos_oe'      
#         )
        
#         if not objetivos_especificos_og.exists():
#             generator.document.add_heading('Objetivos Específicos Relacionados', level=3)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido objetivos específicos para este objetivo general.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('OBJETIVOS ESPECÍFICOS RELACIONADOS', level=3)
#         generator.document.add_paragraph("Objetivos operativos que contribuyen al logro del objetivo general:")
        
#         for i, oe in enumerate(objetivos_especificos_og, 1):
#             # Información del objetivo específico
#             generator.document.add_heading(f'Objetivo Específico {i}: {oe.codigo}', level=4)
            
#             # Tabla de información principal
#             tabla_oe = generator.document.add_table(rows=4, cols=2)
#             tabla_oe.style = 'Light Grid Accent 2'
            
#             datos_oe = [
#                 ('Código', oe.codigo or 'No definido'),
#                 ('Descripción', oe.descripcion or 'No disponible'),
#                 ('Supuestos', oe.supuestos or 'No definidos'),
#                 ('Riesgos', oe.riesgos or 'No identificados')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_oe):
#                 tabla_oe.cell(j, 0).text = campo
#                 tabla_oe.cell(j, 1).text = str(valor)
#                 tabla_oe.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # ✅ CORRECCIÓN: Usar profundidad > 2 en lugar de > 3
#             # El objetivo específico es nivel 3, sus elementos son nivel 4
#             # Si profundidad es 3, debería mostrar nivel 4
#             # Si profundidad es 4, debería mostrar nivel 5
            
#             # ENCADENAR indicadores del objetivo específico si hay profundidad > 2
#             if profundidad > 2:
#                 self._agregar_indicadores_oe(generator, oe)
            
#             # ENCADENAR resultados del objetivo específico si hay profundidad > 2
#             if profundidad > 2:
#                 self._agregar_resultados_oe(generator, oe, profundidad)
            
#             # ENCADENAR productos del objetivo específico si hay profundidad > 2
#             if profundidad > 2:
#                 self._agregar_productos_oe(generator, oe, profundidad)
            
#             generator.document.add_paragraph("―" * 60)
#             generator.document.add_paragraph()

#     def _agregar_resultados_oe(self, generator, objetivo_especifico, profundidad):
#         """Agrega resultados relacionados al objetivo específico"""
#         resultados_oe = objetivo_especifico.resultados_oe.all().prefetch_related(
#             'indicador_res_oe',
#             'productos_res_oe'
#         )
        
#         if not resultados_oe.exists():
#             generator.document.add_heading('Resultados del Objetivo Específico', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido resultados para este objetivo específico.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('RESULTADOS DEL OBJETIVO ESPECÍFICO', level=5)
        
#         for i, resultado in enumerate(resultados_oe, 1):
#             generator.document.add_heading(f'Resultado {i}: {resultado.codigo}', level=6)
            
#             tabla_resultado = generator.document.add_table(rows=4, cols=2)
#             tabla_resultado.style = 'Light List Accent 4'
            
#             datos_resultado = [
#                 ('Código', resultado.codigo or 'No definido'),
#                 ('Descripción', resultado.descripcion or 'No disponible'),
#                 ('Supuestos', resultado.supuestos or 'No definidos'),
#                 ('Riesgos', resultado.riesgos or 'No identificados')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_resultado):
#                 tabla_resultado.cell(j, 0).text = campo
#                 tabla_resultado.cell(j, 1).text = str(valor)
#                 tabla_resultado.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # ✅ CORRECCIÓN: Usar profundidad > 3 en lugar de > 4
#             # El resultado OE es nivel 4, sus elementos son nivel 5
#             # Si profundidad es 4, debería mostrar nivel 5
            
#             # ENCADENAR niveles inferiores si hay profundidad > 3
#             if profundidad > 3:
#                 self._agregar_nivel_5_resultado_oe(generator, resultado, profundidad)
            
#             generator.document.add_paragraph("―" * 40)
#             generator.document.add_paragraph()

#     def _agregar_productos_oe(self, generator, objetivo_especifico, profundidad):
#         """Agrega productos relacionados al objetivo específico"""
#         productos_oe = objetivo_especifico.productos_oe.all().prefetch_related(
#             'proceso_producto_oe'
#         )
        
#         if not productos_oe.exists():
#             generator.document.add_heading('Productos del Objetivo Específico', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido productos para este objetivo específico.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('PRODUCTOS DEL OBJETIVO ESPECÍFICO', level=5)
        
#         for i, producto in enumerate(productos_oe, 1):
#             generator.document.add_heading(f'Producto {i}: {producto.codigo}', level=6)
            
#             tabla_producto = generator.document.add_table(rows=5, cols=2)
#             tabla_producto.style = 'Light List Accent 5'
            
#             datos_producto = [
#                 ('Código', producto.codigo or 'No definido'),
#                 ('Descripción', producto.descripcion or 'No disponible'),
#                 ('Supuestos', producto.supuestos or 'No definidos'),
#                 ('Riesgos', producto.riesgos or 'No identificados'),
#                 ('Entregado', 'Sí' if producto.entregado else 'No')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_producto):
#                 tabla_producto.cell(j, 0).text = campo
#                 tabla_producto.cell(j, 1).text = str(valor)
#                 tabla_producto.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # ENCADENAR procesos del producto si hay profundidad > 4
#             if profundidad > 4:
#                 self._agregar_procesos_producto_oe(generator, producto)
            
#             generator.document.add_paragraph("―" * 40)
#             generator.document.add_paragraph()


#     def _agregar_indicadores_oe(self, generator, objetivo_especifico):
#         """NUEVO: Agrega indicadores relacionados al objetivo específico"""
#         indicadores_oe = objetivo_especifico.indicador_oe.all()
        
#         if not indicadores_oe.exists():
#             generator.document.add_heading('Indicadores del Objetivo Específico', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido indicadores para este objetivo específico.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('INDICADORES DEL OBJETIVO ESPECÍFICO', level=5)
#         generator.document.add_paragraph("Indicadores para medir el avance del objetivo específico:")
        
#         for i, indicador in enumerate(indicadores_oe, 1):
#             generator.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=6)
            
#             # Tabla de información principal del indicador
#             tabla_indicador = generator.document.add_table(rows=8, cols=2)
#             tabla_indicador.style = 'Light List Accent 3'
            
#             datos_indicador = [
#                 ('Código', indicador.codigo or 'No definido'),
#                 ('Descripción', indicador.descripcion or 'No disponible'),
#                 ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
#                 ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
#                 ('Línea Base', indicador.baseline or 'No definida'),
#                 ('Meta Q1', indicador.target_q1 or 'No definida'),
#                 ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
#                 ('Responsable', indicador.responsable or 'No asignado')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_indicador):
#                 tabla_indicador.cell(j, 0).text = campo
#                 tabla_indicador.cell(j, 1).text = str(valor)
#                 tabla_indicador.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # Metas adicionales si existen
#             metas_existen = any([
#                 indicador.target_q2, indicador.target_q3, indicador.target_q4
#             ])
            
#             if metas_existen:
#                 generator.document.add_heading('Metas Adicionales', level=7)
                
#                 tabla_metas = generator.document.add_table(rows=3, cols=2)
#                 tabla_metas.style = 'Light Grid Accent 4'
                
#                 metas = [
#                     ('Meta Q2', indicador.target_q2),
#                     ('Meta Q3', indicador.target_q3),
#                     ('Meta Q4', indicador.target_q4)
#                 ]
                
#                 # Filtrar solo metas que existen
#                 metas_validas = [(periodo, meta) for periodo, meta in metas if meta]
                
#                 for k, (periodo, meta) in enumerate(metas_validas):
#                     tabla_metas.cell(k, 0).text = periodo
#                     tabla_metas.cell(k, 1).text = meta
#                     tabla_metas.cell(k, 0).paragraphs[0].runs[0].bold = True
                
#                 generator.document.add_paragraph()
            
#             generator.document.add_paragraph("―" * 40)
#             generator.document.add_paragraph()

#     def _agregar_resultados_og(self, generator, objetivo_general, profundidad):
#         """Agrega resultados relacionados al objetivo general con niveles inferiores"""
#         resultados_og = ResultadoOG.objects.filter(
#             objetivo_general=objetivo_general
#         ).prefetch_related(
#             'indicador_res_og',
#             'proceso_resultado_og'
#         )
        
#         if not resultados_og.exists():
#             generator.document.add_heading('Resultados Relacionados', level=3)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido resultados para este objetivo general.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('RESULTADOS ESPERADOS', level=3)
#         generator.document.add_paragraph("Resultados estratégicos que se esperan del objetivo general:")
        
#         for i, resultado in enumerate(resultados_og, 1):
#             # Información del resultado
#             generator.document.add_heading(f'Resultado {i}: {resultado.codigo}', level=4)
            
#             # Tabla de información principal
#             tabla_resultado = generator.document.add_table(rows=4, cols=2)
#             tabla_resultado.style = 'Light Grid Accent 3'
            
#             datos_resultado = [
#                 ('Código', resultado.codigo or 'No definido'),
#                 ('Descripción', resultado.descripcion or 'No disponible'),
#                 ('Supuestos', resultado.supuestos or 'No definidos'),
#                 ('Riesgos', resultado.riesgos or 'No identificados')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_resultado):
#                 tabla_resultado.cell(j, 0).text = campo
#                 tabla_resultado.cell(j, 1).text = str(valor)
#                 tabla_resultado.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # ENCADENAR niveles inferiores del resultado OG si hay profundidad > 3
#             if profundidad > 3:
#                 self._agregar_nivel_4_resultado_og(generator, resultado, profundidad)
            
#             generator.document.add_paragraph("―" * 60)
#             generator.document.add_paragraph()

#     def _agregar_procesos_rog(self, generator, resultado_og):
#         """Agrega procesos relacionados al resultado OG"""
#         procesos_rog = resultado_og.proceso_resultado_og.all()
        
#         if not procesos_rog.exists():
#             generator.document.add_heading('Procesos del Resultado OG', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido procesos para este resultado OG.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('PROCESOS DEL RESULTADO OG', level=5)
#         generator.document.add_paragraph("Procesos necesarios para alcanzar el resultado OG:")
        
#         for i, proceso in enumerate(procesos_rog, 1):
#             generator.document.add_heading(f'Proceso {i}: {proceso.codigo}', level=6)
            
#             tabla_proceso = generator.document.add_table(rows=3, cols=2)
#             tabla_proceso.style = 'Light List Accent 2'
            
#             datos_proceso = [
#                 ('Código', proceso.codigo or 'No definido'),
#                 ('Título', proceso.titulo or 'No disponible'),
#                 ('Descripción', proceso.descripcion or 'No disponible')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_proceso):
#                 tabla_proceso.cell(j, 0).text = campo
#                 tabla_proceso.cell(j, 1).text = str(valor)
#                 tabla_proceso.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
#             generator.document.add_paragraph("―" * 50)
#             generator.document.add_paragraph()
            
#     def _agregar_procesos_producto_oe(self, generator, producto_oe):
#         """Agrega procesos relacionados al producto OE"""
#         procesos_poe = producto_oe.proceso_producto_oe.all()
        
#         if procesos_poe.exists():
#             generator.document.add_heading('Procesos del Producto', level=7)
            
#             for proceso in procesos_poe:
#                 generator.document.add_heading(f'Proceso: {proceso.codigo}', level=8)
                
#                 tabla_proceso = generator.document.add_table(rows=3, cols=2)
#                 tabla_proceso.style = 'Table Grid'
                
#                 datos_proceso = [
#                     ('Código', proceso.codigo or 'No definido'),
#                     ('Título', proceso.titulo or 'No disponible'),
#                     ('Descripción', proceso.descripcion or 'No disponible')
#                 ]
                
#                 for i, (campo, valor) in enumerate(datos_proceso):
#                     tabla_proceso.cell(i, 0).text = campo
#                     tabla_proceso.cell(i, 1).text = str(valor)
#                     tabla_proceso.cell(i, 0).paragraphs[0].runs[0].bold = True
                
#                 generator.document.add_paragraph()            
    
#     def _agregar_indicadores_roe(self, generator, resultado_oe):
#         """Agrega indicadores relacionados al resultado OE"""
#         indicadores_roe = resultado_oe.indicador_res_oe.all()
        
#         if not indicadores_roe.exists():
#             generator.document.add_heading('Indicadores del Resultado OE', level=7)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido indicadores para este resultado OE.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('INDICADORES DEL RESULTADO OE', level=7)
#         generator.document.add_paragraph("Indicadores para medir el avance del resultado OE:")
        
#         for i, indicador in enumerate(indicadores_roe, 1):
#             generator.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=8)
            
#             # Tabla de información principal del indicador
#             tabla_indicador = generator.document.add_table(rows=8, cols=2)
#             tabla_indicador.style = 'Table Grid'
            
#             datos_indicador = [
#                 ('Código', indicador.codigo or 'No definido'),
#                 ('Descripción', indicador.descripcion or 'No disponible'),
#                 ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
#                 ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
#                 ('Línea Base', indicador.baseline or 'No definida'),
#                 ('Meta Q1', indicador.target_q1 or 'No definida'),
#                 ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
#                 ('Responsable', indicador.responsable or 'No asignado')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_indicador):
#                 tabla_indicador.cell(j, 0).text = campo
#                 tabla_indicador.cell(j, 1).text = str(valor)
#                 tabla_indicador.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
            
#             # Metas adicionales si existen
#             metas_existen = any([
#                 indicador.target_q2, indicador.target_q3, indicador.target_q4
#             ])
            
#             if metas_existen:
#                 generator.document.add_heading('Metas Adicionales', level=9)
                
#                 tabla_metas = generator.document.add_table(rows=3, cols=2)
#                 tabla_metas.style = 'Table Grid'
                
#                 metas = [
#                     ('Meta Q2', indicador.target_q2),
#                     ('Meta Q3', indicador.target_q3),
#                     ('Meta Q4', indicador.target_q4)
#                 ]
                
#                 # Filtrar solo metas que existen
#                 metas_validas = [(periodo, meta) for periodo, meta in metas if meta]
                
#                 for k, (periodo, meta) in enumerate(metas_validas):
#                     tabla_metas.cell(k, 0).text = periodo
#                     tabla_metas.cell(k, 1).text = meta
#                     tabla_metas.cell(k, 0).paragraphs[0].runs[0].bold = True
                
#                 generator.document.add_paragraph()
            
#             generator.document.add_paragraph("―" * 30)
#             generator.document.add_paragraph()

#     def _agregar_productos_roe(self, generator, resultado_oe):
#         """Agrega productos relacionados al resultado OE"""
#         productos_roe = resultado_oe.productos_res_oe.all()
        
#         if not productos_roe.exists():
#             generator.document.add_heading('Productos del Resultado OE', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido productos para este resultado OE.").italic = True
#             generator.document.add_paragraph()
#             return
        
#         generator.document.add_heading('PRODUCTOS DEL RESULTADO OE', level=5)
#         generator.document.add_paragraph("Productos esperados que contribuyen al resultado OE:")
        
#         for i, producto in enumerate(productos_roe, 1):
#             generator.document.add_heading(f'Producto {i}: {producto.codigo}', level=6)
            
#             # Tabla de información principal
#             tabla_producto = generator.document.add_table(rows=5, cols=2)
#             tabla_producto.style = 'Light List Accent 4'
            
#             datos_producto = [
#                 ('Código', producto.codigo or 'No definido'),
#                 ('Descripción', producto.descripcion or 'No disponible'),
#                 ('Supuestos', producto.supuestos or 'No definidos'),
#                 ('Riesgos', producto.riesgos or 'No identificados'),
#                 ('Entregado', '✅ Sí' if producto.entregado else '⏳ No')
#             ]
            
#             for j, (campo, valor) in enumerate(datos_producto):
#                 tabla_producto.cell(j, 0).text = campo
#                 tabla_producto.cell(j, 1).text = str(valor)
#                 tabla_producto.cell(j, 0).paragraphs[0].runs[0].bold = True
            
#             generator.document.add_paragraph()
#             generator.document.add_paragraph("―" * 50)
#             generator.document.add_paragraph()

#     def _agregar_nivel_4_resultado_og(self, generator, resultado_og, profundidad):
#         """Agrega nivel 4: Indicadores y Procesos del Resultado OG"""
        
#         # INDICADORES del Resultado OG (Nivel 4)
#         indicadores_rog = resultado_og.indicador_res_og.all()
#         if indicadores_rog.exists():
#             generator.document.add_heading('Indicadores del Resultado', level=5)
#             generator.document.add_paragraph("Indicadores para medir el avance del resultado:")
            
#             for idx, indicador in enumerate(indicadores_rog, 1):
#                 generator.document.add_heading(f'Indicador {idx}: {indicador.codigo}', level=6)
                
#                 # Tabla de información principal del indicador
#                 tabla_indicador = generator.document.add_table(rows=8, cols=2)
#                 tabla_indicador.style = 'Light List Accent 1'
                
#                 datos_indicador = [
#                     ('Código', indicador.codigo or 'No definido'),
#                     ('Descripción', indicador.descripcion or 'No disponible'),
#                     ('Tipo', indicador.get_tipo_display() if indicador.tipo else 'No definido'),
#                     ('Frecuencia', indicador.get_frecuencia_display() if indicador.frecuencia else 'No definida'),
#                     ('Línea Base', indicador.baseline or 'No definida'),
#                     ('Meta Q1', indicador.target_q1 or 'No definida'),
#                     ('Fuente Verificación', indicador.fuente_verificacion or 'No definida'),
#                     ('Responsable', indicador.responsable or 'No asignado')
#                 ]
                
#                 for i, (campo, valor) in enumerate(datos_indicador):
#                     tabla_indicador.cell(i, 0).text = campo
#                     tabla_indicador.cell(i, 1).text = str(valor)
#                     tabla_indicador.cell(i, 0).paragraphs[0].runs[0].bold = True
                
#                 generator.document.add_paragraph()
                
#                 # Metas del indicador si existen
#                 metas_existen = any([
#                     indicador.target_q2, indicador.target_q3, indicador.target_q4
#                 ])
                
#                 if metas_existen:
#                     generator.document.add_heading('Metas Adicionales', level=7)
                    
#                     tabla_metas = generator.document.add_table(rows=4, cols=2)
#                     tabla_metas.style = 'Light Grid Accent 2'
                    
#                     metas = [
#                         ('Meta Q2', indicador.target_q2),
#                         ('Meta Q3', indicador.target_q3),
#                         ('Meta Q4', indicador.target_q4)
#                     ]
                    
#                     # Filtrar solo metas que existen
#                     metas_validas = [(periodo, meta) for periodo, meta in metas if meta]
                    
#                     for i, (periodo, meta) in enumerate(metas_validas):
#                         tabla_metas.cell(i, 0).text = periodo
#                         tabla_metas.cell(i, 1).text = meta
#                         tabla_metas.cell(i, 0).paragraphs[0].runs[0].bold = True
                    
#                     generator.document.add_paragraph()
        
#         # ✅ PROCESOS del Resultado OG (Nivel 4)
#         self._agregar_procesos_rog(generator, resultado_og)
        
#         # Si no hay elementos en el nivel 4
#         if not indicadores_rog.exists() and not resultado_og.proceso_resultado_og.exists():
#             generator.document.add_heading('Elementos de Seguimiento', level=5)
#             p = generator.document.add_paragraph()
#             p.add_run("No se han definido indicadores ni procesos para este resultado.").italic = True
#             generator.document.add_paragraph()
    
#     def _agregar_nivel_5_resultado_oe(self, generator, resultado_oe, profundidad):
#         """Agrega nivel 5 para resultado OE: Indicadores, Productos, Procesos"""
        
#         # ✅ Indicadores ROE - usar método existente
#         self._agregar_indicadores_roe(generator, resultado_oe)
        
#         # ✅ Productos ROE - usar el método específico que ya creaste
#         self._agregar_productos_roe(generator, resultado_oe)
        
#         # ✅ Procesos ROE - mantener esta parte
#         procesos_roe = resultado_oe.proceso_resultado_oe.all()
#         if procesos_roe.exists():
#             generator.document.add_heading('Procesos del Resultado OE', level=7)
#             generator.document.add_paragraph("Procesos necesarios para alcanzar el resultado OE:")
            
#             for proceso in procesos_roe:
#                 generator.document.add_heading(f'Proceso: {proceso.codigo}', level=8)
                
#                 tabla_proceso = generator.document.add_table(rows=3, cols=2)
#                 tabla_proceso.style = 'Table Grid'
                
#                 datos_proceso = [
#                     ('Código', proceso.codigo or 'No definido'),
#                     ('Título', proceso.titulo or 'No disponible'),
#                     ('Descripción', proceso.descripcion or 'No disponible')
#                 ]
                
#                 for i, (campo, valor) in enumerate(datos_proceso):
#                     tabla_proceso.cell(i, 0).text = campo
#                     tabla_proceso.cell(i, 1).text = str(valor)
#                     tabla_proceso.cell(i, 0).paragraphs[0].runs[0].bold = True
                
#                 generator.document.add_paragraph()

#     def generar_y_descargar(self, modelo, objeto_id, profundidad=2):
#         """Genera y descarga el reporte encadenado"""
#         try:
#             modelos_directos = [
#                 'objetivoespecificoog', 'resultadoog', 'resultadooe', 'productooe',
#                 'indicadorog', 'indicadorrog', 'indicadoroe', 'indicadorroe', 'productoroe',
#                 'procesorog', 'procesoroe', 'procesopoe'  # ✅ NUEVOS
#             ]
            
#             if modelo in modelos_directos:
#                 # Para estos modelos, manejo directo
#                 generator = self.generators_registry[modelo]['generator_class']()
#                 if modelo == 'objetivoespecificoog':
#                     #buffer = generator.generar_reporte_objetivo_especifico_og(objeto_id)
#                     buffer = generator.generar_reporte_objetivo_especifico_og(objeto_id, profundidad)
#                 elif modelo == 'resultadoog':
#                     buffer = generator.generar_reporte_resultado_og(objeto_id)
#                 elif modelo == 'resultadooe':
#                     buffer = generator.generar_reporte_resultado_oe(objeto_id)
#                 elif modelo == 'productooe':
#                     buffer = generator.generar_reporte_producto_oe(objeto_id)
#                 elif modelo == 'indicadorog':
#                     buffer = generator.generar_reporte_indicador_og(objeto_id)
#                 elif modelo == 'indicadorrog':
#                     buffer = generator.generar_reporte_indicador_rog(objeto_id)    
#                 elif modelo == 'indicadoroe':
#                     buffer = generator.generar_reporte_indicador_oe(objeto_id)
#                 elif modelo == 'indicadorroe':
#                     buffer = generator.generar_reporte_indicador_roe(objeto_id)
#                 elif modelo == 'productoroe':
#                     buffer = generator.generar_reporte_producto_roe(objeto_id)
#                 elif modelo in ['procesorog', 'procesoroe', 'procesopoe']:  # ✅ NUEVO
#                     buffer = generator.generar_reporte_proceso(objeto_id, modelo)
#             else:
#                 generator = self.generar_reporte_encadenado(modelo, objeto_id, profundidad)
#                 buffer = generator._guardar_documento()
            
#             response = HttpResponse(
#                 buffer.getvalue(),
#                 content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
#             )
#             response['Content-Disposition'] = f'attachment; filename="reporte_encadenado_{modelo}_{objeto_id}.docx"'
            
#             return response
            
#         except Exception as e:
#             raise ValueError(f"Error generando reporte: {str(e)}")
from django.http import HttpResponse
import os
import django

# Configurar Django explícitamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

from spme_estructuracion_proyecto.models import (
    Proyecto, 
    ObjetivoGeneralProyecto, 
    ObjetivoEspecificoProyecto,
    ResultadoOG,
    IndicadorObjetivoGeneral,
    IndicadorResultadoObjGral,
    Proceso
)
from ..generators.proyecto_generator import ProyectoGenerator
from ..generators.objetivo_general_generator import ObjetivoGeneralGenerator
from ..generators.objetivo_especifico_og_generator import ObjetivoEspecificoOGGenerator
from ..generators.resultado_og_generator import ResultadoOGGenerator
from ..generators.indicador_og_generator import IndicadorOGGenerator
from ..generators.indicador_rog_generator import IndicadorROGGenerator

class ChainComposer:
    """
    Orquestador principal para encadenamiento de reportes
    """
    
    def __init__(self):
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
            'indicadorog': {
                'generator_class': IndicadorOGGenerator,
                'nivel': 3
            },
            'indicadorrog': {
                'generator_class': IndicadorROGGenerator,
                'nivel': 4
            }
        }
    
    def generar_reporte_encadenado(self, modelo, objeto_id, profundidad=2):
        """
        Genera reporte encadenado
        """
        if modelo not in self.generators_registry:
            raise ValueError(f"Generador para '{modelo}' no registrado")
        
        # Obtener generador
        generator_class = self.generators_registry[modelo]['generator_class']
        generator = generator_class()
        
        # Generar reporte basado en el modelo
        if modelo == 'proyecto':
            proyecto = Proyecto.objects.get(id=objeto_id)
            
            # Generar secciones principales del proyecto
            generator._agregar_portada(proyecto)
            generator._agregar_informacion_basica(proyecto)
            generator._agregar_presupuesto_estado(proyecto)
            generator._agregar_relaciones(proyecto)
            
            # ENCADENAR objetivos generales si hay profundidad > 1
            if profundidad > 1:
                objetivos_generales = ObjetivoGeneralProyecto.objects.filter(proyecto=proyecto)
                if objetivos_generales.exists():
                    generator.document.add_heading('OBJETIVOS GENERALES ENCADENADOS', level=1)
                    
                    for og in objetivos_generales:
                        # Agregar información del objetivo general al documento
                        generator.document.add_heading(f"Objetivo General: {og.codigo}", level=2)
                        
                        p_desc = generator.document.add_paragraph()
                        p_desc.add_run("Descripción: ").bold = True
                        p_desc.add_run(og.descripcion or "No disponible")
                        
                        if og.supuestos:
                            p_sup = generator.document.add_paragraph()
                            p_sup.add_run("Supuestos: ").bold = True
                            p_sup.add_run(og.supuestos)
                            
                        if og.riesgos:
                            p_risk = generator.document.add_paragraph()
                            p_risk.add_run("Riesgos: ").bold = True
                            p_risk.add_run(og.riesgos)
                        
                        # ENCADENAR indicadores del objetivo general si hay profundidad > 2
                        if profundidad > 2:
                            self._agregar_indicadores_og(generator, og)
                        
                        # ENCADENAR objetivos específicos del objetivo general si hay profundidad > 2
                        if profundidad > 2:
                            self._agregar_objetivos_especificos_og(generator, og)
                        
                        # ENCADENAR resultados del objetivo general si hay profundidad > 2
                        if profundidad > 2:
                            self._agregar_resultados_og(generator, og, profundidad)
                        
                        generator.document.add_paragraph()  # Espacio entre objetivos
                        
        elif modelo == 'objetivogeneral':
            # Para objetivo general, generar su reporte individual
            objetivo_general = ObjetivoGeneralProyecto.objects.get(id=objeto_id)
            generator._agregar_portada(objetivo_general)
            generator._agregar_informacion_principal(objetivo_general)
            generator._agregar_analisis_riesgos(objetivo_general)
            
            # ENCADENAR indicadores del objetivo general si hay profundidad > 1
            if profundidad > 1:
                self._agregar_indicadores_og(generator, objetivo_general)
            
            # ENCADENAR objetivos específicos del objetivo general si hay profundidad > 1
            if profundidad > 1:
                self._agregar_objetivos_especificos_og(generator, objetivo_general)
            
            # ENCADENAR resultados del objetivo general si hay profundidad > 1
            if profundidad > 1:
                self._agregar_resultados_og(generator, objetivo_general, profundidad)
        
        elif modelo == 'objetivoespecificoog':
            # Para objetivo específico del OG, usar su generador específico
            return generator.generar_reporte_objetivo_especifico_og(objeto_id)
        
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
        
        elif modelo == 'indicadorog':
            # Para indicador OG, usar su generador específico
            return generator.generar_reporte_indicador_og(objeto_id)
        
        elif modelo == 'indicadorrog':
            # Para indicador ROG, usar su generador específico
            return generator.generar_reporte_indicador_rog(objeto_id)
        
        return generator

    def _agregar_indicadores_og(self, generator, objetivo_general):
        """Agrega indicadores relacionados al objetivo general"""
        indicadores_og = IndicadorObjetivoGeneral.objects.filter(
            objetivo_general=objetivo_general
        )
        
        if not indicadores_og.exists():
            generator.document.add_heading('Indicadores del Objetivo General', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido indicadores para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('INDICADORES DEL OBJETIVO GENERAL', level=3)
        generator.document.add_paragraph("Indicadores para medir el avance del objetivo general:")
        
        for i, indicador in enumerate(indicadores_og, 1):
            # Información del indicador
            generator.document.add_heading(f'Indicador {i}: {indicador.codigo}', level=4)
            
            # Tabla de información principal
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

    def _agregar_objetivos_especificos_og(self, generator, objetivo_general):
        """Agrega objetivos específicos relacionados al objetivo general"""
        objetivos_especificos_og = ObjetivoEspecificoProyecto.objects.filter(
            objetivo_general=objetivo_general
        )
        
        if not objetivos_especificos_og.exists():
            generator.document.add_heading('Objetivos Específicos Relacionados', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido objetivos específicos para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('OBJETIVOS ESPECÍFICOS RELACIONADOS', level=3)
        generator.document.add_paragraph("Objetivos operativos que contribuyen al logro del objetivo general:")
        
        for i, oe in enumerate(objetivos_especificos_og, 1):
            # Información del objetivo específico
            generator.document.add_heading(f'Objetivo Específico {i}: {oe.codigo}', level=4)
            
            # Tabla de información principal
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
        """Agrega resultados relacionados al objetivo general con niveles inferiores"""
        resultados_og = ResultadoOG.objects.filter(
            objetivo_general=objetivo_general
        ).prefetch_related(
            'indicador_res_og',
            'proceso_resultado_og'
        )
        
        if not resultados_og.exists():
            generator.document.add_heading('Resultados Relacionados', level=3)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido resultados para este objetivo general.").italic = True
            generator.document.add_paragraph()
            return
        
        generator.document.add_heading('RESULTADOS ESPERADOS', level=3)
        generator.document.add_paragraph("Resultados estratégicos que se esperan del objetivo general:")
        
        for i, resultado in enumerate(resultados_og, 1):
            # Información del resultado
            generator.document.add_heading(f'Resultado {i}: {resultado.codigo}', level=4)
            
            # Tabla de información principal
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
            
            # ENCADENAR niveles inferiores del resultado OG si hay profundidad > 3
            if profundidad > 3:
                self._agregar_nivel_4_resultado_og(generator, resultado, profundidad)
            
            generator.document.add_paragraph("―" * 60)
            generator.document.add_paragraph()

    def _agregar_nivel_4_resultado_og(self, generator, resultado_og, profundidad):
        """Agrega nivel 4: Indicadores y Procesos del Resultado OG"""
        
        # INDICADORES del Resultado OG (Nivel 4)
        indicadores_rog = resultado_og.indicador_res_og.all()
        if indicadores_rog.exists():
            generator.document.add_heading('Indicadores del Resultado', level=5)
            generator.document.add_paragraph("Indicadores para medir el avance del resultado:")
            
            for idx, indicador in enumerate(indicadores_rog, 1):
                generator.document.add_heading(f'Indicador {idx}: {indicador.codigo}', level=6)
                
                # Tabla de información principal del indicador
                tabla_indicador = generator.document.add_table(rows=8, cols=2)
                tabla_indicador.style = 'Light List Accent 1'
                
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
                
                for i, (campo, valor) in enumerate(datos_indicador):
                    tabla_indicador.cell(i, 0).text = campo
                    tabla_indicador.cell(i, 1).text = str(valor)
                    tabla_indicador.cell(i, 0).paragraphs[0].runs[0].bold = True
                
                generator.document.add_paragraph()
                
                # Metas del indicador si existen
                metas_existen = any([
                    indicador.target_q2, indicador.target_q3, indicador.target_q4
                ])
                
                if metas_existen:
                    generator.document.add_heading('Metas Adicionales', level=7)
                    
                    tabla_metas = generator.document.add_table(rows=4, cols=2)
                    tabla_metas.style = 'Light Grid Accent 2'
                    
                    metas = [
                        ('Meta Q2', indicador.target_q2),
                        ('Meta Q3', indicador.target_q3),
                        ('Meta Q4', indicador.target_q4)
                    ]
                    
                    # Filtrar solo metas que existen
                    metas_validas = [(periodo, meta) for periodo, meta in metas if meta]
                    
                    for i, (periodo, meta) in enumerate(metas_validas):
                        tabla_metas.cell(i, 0).text = periodo
                        tabla_metas.cell(i, 1).text = meta
                        tabla_metas.cell(i, 0).paragraphs[0].runs[0].bold = True
                    
                    generator.document.add_paragraph()
        
        # PROCESOS del Resultado OG (Nivel 4)
        procesos_rog = resultado_og.proceso_resultado_og.all()
        if procesos_rog.exists():
            generator.document.add_heading('Procesos del Resultado', level=5)
            generator.document.add_paragraph("Procesos necesarios para alcanzar el resultado:")
            
            for proceso in procesos_rog:
                generator.document.add_heading(f'Proceso: {proceso.codigo}', level=6)
                
                tabla_proceso = generator.document.add_table(rows=3, cols=2)
                tabla_proceso.style = 'Light List Accent 2'
                
                datos_proceso = [
                    ('Código', proceso.codigo or 'No definido'),
                    ('Título', proceso.titulo or 'No disponible'),
                    ('Descripción', proceso.descripcion or 'No disponible')
                ]
                
                for i, (campo, valor) in enumerate(datos_proceso):
                    tabla_proceso.cell(i, 0).text = campo
                    tabla_proceso.cell(i, 1).text = str(valor)
                    tabla_proceso.cell(i, 0).paragraphs[0].runs[0].bold = True
                
                generator.document.add_paragraph()
        
        # Si no hay elementos en el nivel 4
        if not indicadores_rog.exists() and not procesos_rog.exists():
            generator.document.add_heading('Elementos de Seguimiento', level=5)
            p = generator.document.add_paragraph()
            p.add_run("No se han definido indicadores ni procesos para este resultado.").italic = True
            generator.document.add_paragraph()
    
    def generar_y_descargar(self, modelo, objeto_id, profundidad=2):
        """Genera y descarga el reporte encadenado"""
        try:
            if modelo in ['objetivoespecificoog', 'resultadoog', 'indicadorog', 'indicadorrog']:
                # Para estos modelos, manejo directo
                generator = self.generators_registry[modelo]['generator_class']()
                if modelo == 'objetivoespecificoog':
                    buffer = generator.generar_reporte_objetivo_especifico_og(objeto_id)
                elif modelo == 'resultadoog':
                    buffer = generator.generar_reporte_resultado_og(objeto_id)
                elif modelo == 'indicadorog':
                    buffer = generator.generar_reporte_indicador_og(objeto_id)
                else:  # indicadorrog
                    buffer = generator.generar_reporte_indicador_rog(objeto_id)
            else:
                generator = self.generar_reporte_encadenado(modelo, objeto_id, profundidad)
                buffer = generator._guardar_documento()
            
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="reporte_encadenado_{modelo}_{objeto_id}.docx"'
            
            return response
            
        except Exception as e:
            raise ValueError(f"Error generando reporte: {str(e)}")
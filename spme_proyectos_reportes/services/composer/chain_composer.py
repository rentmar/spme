from django.http import HttpResponse
import os
import django

# Configurar Django explícitamente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

from spme_estructuracion_proyecto.models import Proyecto, ObjetivoGeneralProyecto
from ..generators.proyecto_generator import ProyectoGenerator
from ..generators.objetivo_general_generator import ObjetivoGeneralGenerator

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
                        
                        generator.document.add_paragraph()  # Espacio entre objetivos
                        
        elif modelo == 'objetivogeneral':
            # Para objetivo general, generar solo su reporte individual
            objetivo_general = ObjetivoGeneralProyecto.objects.get(id=objeto_id)
            generator._agregar_portada(objetivo_general)
            generator._agregar_informacion_principal(objetivo_general)
            generator._agregar_analisis_riesgos(objetivo_general)
        
        return generator
    
    def generar_y_descargar(self, modelo, objeto_id, profundidad=2):
        """Genera y descarga el reporte encadenado"""
        generator = self.generar_reporte_encadenado(modelo, objeto_id, profundidad)
        buffer = generator._guardar_documento()
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_encadenado_{modelo}_{objeto_id}.docx"'
        
        return response
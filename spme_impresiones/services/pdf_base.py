import os
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
import tempfile
from datetime import datetime

class BasePDFGenerator:
    """
    Clase base para generación de PDFs con funcionalidades comunes
    """
    
    # Configuración común
    DEFAULT_TEMPLATE = 'spme_impresiones/base_template.html'
    DEFAULT_FILENAME_PREFIX = 'documento'
    
    def __init__(self):
        self.template_name = None
        self.context = {}
        self.filename = None
        
    def get_common_context(self):
        """
        Retorna el contexto común para todos los PDFs
        """
        return {
            'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'anio_actual': datetime.now().year,
            'institucion_nombre': 'UNIDAD TÉCNICA DE ASESORAMIENTO SOCIAL - UNITAS',
            'institucion_direccion': 'Calle José María Larrea Nº 269 (entre calles Ecuador y Sánchez Lima)',
            'institucion_telefono': '+591 2 242 0469',
            'institucion_email': 'unitas@unitas.org',
            'sistema_nombre': 'Sistema de Gestión de Proyectos - SGP',
            'version_sistema': '1.0',
        }
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para cada tipo de solicitud
        Debe ser implementado por las clases hijas
        """
        raise NotImplementedError("Este método debe ser implementado por las clases hijas")
    
    def get_template_name(self):
        """
        Retorna el nombre de la plantilla a usar
        """
        return self.template_name
    
    def generate_filename(self, obj):
        """
        Genera el nombre del archivo PDF
        """
        if self.filename:
            return self.filename
            
        tipo = self.__class__.__name__.replace('PDFGenerator', '')
        numero = obj.numeroFormulario or f"{obj.id:04d}"
        return f"{tipo}_{numero}.pdf"
    
    def render_to_pdf(self, template_name, context):
        """
        Método común para renderizar HTML a PDF
        """
        try:
            # Combinar contexto común con específico
            full_context = {**self.get_common_context(), **context}
            
            # Renderizar la plantilla HTML
            html_string = render_to_string(template_name, full_context)
            
            # Configurar fuentes
            font_config = FontConfiguration()
            
            # Generar PDF
            html = HTML(string=html_string, base_url=settings.BASE_DIR)
            
            # Crear archivo temporal para el PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                html.write_pdf(tmp_file.name, font_config=font_config)
                
                # Leer el contenido del PDF
                with open(tmp_file.name, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                
                # Limpiar archivo temporal
                os.unlink(tmp_file.name)
            
            return pdf_content
            
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            raise
    
    def generate(self, obj, response_type='http'):
        """
        Método principal para generar el PDF
        """
        # Preparar el contexto específico
        specific_context = self.prepare_context(obj)
        
        # Obtener nombre de plantilla
        template_name = self.get_template_name()
        
        # Generar PDF
        pdf_content = self.render_to_pdf(template_name, specific_context)
        
        if response_type == 'http':
            # Crear respuesta HTTP
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{self.generate_filename(obj)}"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        elif response_type == 'bytes':
            # Retornar bytes del PDF
            return pdf_content
        else:
            raise ValueError(f"Tipo de respuesta no válido: {response_type}")
    
    def generate_multiple(self, objects, filename="documentos_combinados.pdf"):
        """
        Genera múltiples PDFs y los combina (implementación básica)
        """
        # Por ahora, generamos solo el primero
        # Se puede expandir para combinar múltiples PDFs
        if objects:
            return self.generate(objects[0])
        return None
from django.http import HttpResponse
from ..base.base_report_service import BaseReportService
from spme_estructuracion_proyecto.models import ObjetivoEspecificoProyecto

class ObjetivoEspecificoOGGenerator(BaseReportService):
    def __init__(self):
        super().__init__()
    
    def generar_reporte_objetivo_especifico_og(self, objetivo_especifico_id):
        """Genera reporte individual del objetivo específico del objetivo general"""
        try:
            objetivo_especifico = ObjetivoEspecificoProyecto.objects.select_related(
                'objetivo_general',
                'proyecto'
            ).get(id=objetivo_especifico_id)
            
            self._agregar_portada(objetivo_especifico)
            self._agregar_informacion_principal(objetivo_especifico)
            self._agregar_analisis_riesgos(objetivo_especifico)
            self._agregar_vinculaciones(objetivo_especifico)
            
            return self._guardar_documento()
            
        except ObjetivoEspecificoProyecto.DoesNotExist:
            raise ValueError(f"Objetivo Específico con ID {objetivo_especifico_id} no encontrado")
    
    def _agregar_portada(self, objetivo_especifico):
        """Portada del reporte de objetivo específico"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        titulo = self.document.add_heading('REPORTE DE OBJETIVO ESPECÍFICO', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        self.document.add_paragraph()
        
        # Información principal de portada - MANEJO SEGURO de None
        info_portada = [
            ('Código del Objetivo:', objetivo_especifico.codigo),
            ('Objetivo General:', self._obtener_codigo_objetivo_general(objetivo_especifico)),
            ('Proyecto:', self._obtener_info_proyecto(objetivo_especifico)),
        ]
        
        for etiqueta, valor in info_portada:
            if valor:
                p = self.document.add_paragraph()
                p.add_run(etiqueta).bold = True
                p.add_run(f' {valor}')
        
        self.document.add_page_break()
    
    def _obtener_codigo_objetivo_general(self, objetivo_especifico):
        """Obtiene el código del objetivo general de forma segura"""
        if objetivo_especifico.objetivo_general and objetivo_especifico.objetivo_general.codigo:
            return objetivo_especifico.objetivo_general.codigo
        return 'No vinculado a objetivo general'
    
    def _obtener_info_proyecto(self, objetivo_especifico):
        """Obtiene información del proyecto de forma segura"""
        if objetivo_especifico.proyecto:
            return f"{objetivo_especifico.proyecto.codigo} - {objetivo_especifico.proyecto.titulo}"
        return 'Proyecto no asignado'
    
    def _agregar_informacion_principal(self, objetivo_especifico):
        """Sección de información principal"""
        self._agregar_seccion('INFORMACIÓN PRINCIPAL', 1)
        
        # Determinar tipo de objetivo específico
        tipo_objetivo = 'Objetivo Específico de Objetivo General' if objetivo_especifico.objetivo_general else 'Objetivo Específico Directo del Proyecto'
        
        datos_principales = [
            ('Código', objetivo_especifico.codigo or 'No definido'),
            ('Descripción', objetivo_especifico.descripcion or 'No disponible'),
            ('Tipo', tipo_objetivo),
            ('Nivel', 'Operativo/Táctico')
        ]
        
        self._agregar_tabla_datos('Datos del Objetivo Específico', datos_principales)
    
    def _agregar_analisis_riesgos(self, objetivo_especifico):
        """Sección de análisis de riesgos y supuestos"""
        self._agregar_seccion('ANÁLISIS OPERATIVO', 1)
        
        # Supuestos
        if objetivo_especifico.supuestos:
            self.document.add_heading('Supuestos Operativos', level=2)
            p_supuestos = self.document.add_paragraph(objetivo_especifico.supuestos)
            p_supuestos.style = 'List Bullet'
            self.document.add_paragraph()
        
        # Riesgos
        if objetivo_especifico.riesgos:
            self.document.add_heading('Riesgos Operativos', level=2)
            p_riesgos = self.document.add_paragraph(objetivo_especifico.riesgos)
            p_riesgos.style = 'List Bullet'
            self.document.add_paragraph()
        
        # Si no hay información
        if not objetivo_especifico.supuestos and not objetivo_especifico.riesgos:
            p = self.document.add_paragraph()
            p.add_run('No se han definido supuestos ni riesgos para este objetivo específico.').italic = True
    
    def _agregar_vinculaciones(self, objetivo_especifico):
        """Sección de vinculaciones"""
        self._agregar_seccion('VINCULACIONES', 1)
        
        vinculaciones = []
        
        # Objetivo General
        if objetivo_especifico.objetivo_general:
            desc_og = objetivo_especifico.objetivo_general.descripcion
            vinculaciones.append(('Objetivo General', 
                                f"{objetivo_especifico.objetivo_general.codigo} - {desc_og[:50]}..." if desc_og else objetivo_especifico.objetivo_general.codigo))
        else:
            vinculaciones.append(('Objetivo General', 'No vinculado'))
        
        # Proyecto
        if objetivo_especifico.proyecto:
            vinculaciones.append(('Proyecto', 
                                f"{objetivo_especifico.proyecto.codigo} - {objetivo_especifico.proyecto.titulo}"))
        else:
            vinculaciones.append(('Proyecto', 'No asignado'))
        
        if vinculaciones:
            self._agregar_tabla_datos('Relaciones del Objetivo', vinculaciones)
    
    def generar_y_descargar_individual(self, objetivo_especifico_id):
        """Genera y descarga SOLO el objetivo específico"""
        buffer = self.generar_reporte_objetivo_especifico_og(objetivo_especifico_id)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_objetivo_especifico_{objetivo_especifico_id}.docx"'
        
        return response
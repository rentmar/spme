import os
from django.conf import settings
from .base_report_service import BaseReportService
from spme_proyectos_reportes.repositories.proyecto_repository import ProyectoRepository
from .objetivo_general_report_service import ObjetivoGeneralReportService
from .objetivo_especifico_report_service import ObjetivoEspecificoReportService

class ProyectoReportService(BaseReportService):
    def __init__(self, proyecto_id):
        super().__init__()
        self.proyecto = ProyectoRepository.get_full_proyecto(proyecto_id)

    def build_report(self):
        p = self.proyecto
        self.add_title(f"Proyecto: {p.codigo} - {p.titulo}")
        self.add_paragraph(f"Descripción: {p.descripcion}")
        self.add_key_value("Presupuesto", p.presupuesto)
        self.add_key_value("Estado", p.get_estado_display())
        self.add_key_value("Creado por", p.creado_por)

        # Instancias gestoras
        self.add_title("Instancias Gestoras", level=2)
        self.add_bullet_list([ig.instancia for ig in p.instancia_gestora.all()])

        # Financiadores
        self.add_title("Procedencia de Fondos", level=2)
        self.add_bullet_list([pf.financiera for pf in p.procedencia_fondos.all()])

        # Objetivo General
        if hasattr(p, "objetivo_general") and p.objetivo_general:
            self.add_title("Objetivo General", level=2)
            og_service = ObjetivoGeneralReportService(p.objetivo_general)
            og_service.build_section(self.doc)

        # Objetivos Específicos del Proyecto
        objetivos = p.objetivos_especificos.all()
        if objetivos.exists():
            self.add_title("Objetivos Específicos del Proyecto", level=2)
            for oe in objetivos:
                oe_service = ObjetivoEspecificoReportService(oe)
                oe_service.build_section(self.doc)

        # Guardar documento
        filename = os.path.join(settings.MEDIA_ROOT, f"reporte_proyecto_{p.codigo}.docx")
        self.save(filename)
        return filename

from .base_report_service import BaseReportService
from .resultadoog_report_service import ResultadoOGReportService
from .objetivo_especifico_report_service import ObjetivoEspecificoReportService

class ObjetivoGeneralReportService(BaseReportService):
    def __init__(self, objetivo_general):
        super().__init__()
        self.og = objetivo_general

    def build_section(self, doc=None):
        target = doc or self.doc

        target.add_heading("Objetivo General", level=2)
        target.add_paragraph(self.og.descripcion)

        # Indicadores OG
        indicadores = self.og.indicador_og.all()
        if indicadores.exists():
            target.add_heading("Indicadores del Objetivo General", level=3)
            for ind in indicadores:
                target.add_paragraph(f"• {ind.codigo}: {ind.descripcion}")

        # Resultados OG
        resultados = self.og.resultados_og.all()
        if resultados.exists():
            target.add_heading("Resultados del Objetivo General", level=3)
            for r in resultados:
                rog_service = ResultadoOGReportService(r)
                rog_service.build_section(target)

        # Objetivos específicos relacionados al OG
        objetivos_especificos = self.og.objetivos_especificos_og.all()
        if objetivos_especificos.exists():
            target.add_heading("Objetivos Específicos (de OG)", level=3)
            for oe in objetivos_especificos:
                oe_service = ObjetivoEspecificoReportService(oe)
                oe_service.build_section(target)

        if not doc:
            filename = f"reporte_og_{self.og.codigo}.docx"
            self.save(filename)
            return filename

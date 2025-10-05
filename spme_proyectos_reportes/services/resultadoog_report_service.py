from .base_report_service import BaseReportService
from .proceso_report_service import ProcesoReportService

class ResultadoOGReportService(BaseReportService):
    def __init__(self, resultado):
        super().__init__()
        self.r = resultado

    def build_section(self, doc=None):
        target = doc or self.doc

        target.add_heading(f"Resultado OG {self.r.codigo}", level=4)
        target.add_paragraph(self.r.descripcion)

        # Indicadores del Resultado OG
        indicadores = self.r.indicador_res_og.all()
        if indicadores.exists():
            target.add_heading("Indicadores del Resultado OG", level=5)
            for ind in indicadores:
                target.add_paragraph(f"• {ind.codigo}: {ind.descripcion}")

        # Procesos asociados
        procesos = self.r.proceso_resultado_og.all()
        if procesos.exists():
            target.add_heading("Procesos del Resultado OG", level=5)
            for p in procesos:
                p_service = ProcesoReportService(p)
                p_service.build_section(target)

        if not doc:
            filename = f"reporte_resultado_og_{self.r.codigo}.docx"
            self.save(filename)
            return filename

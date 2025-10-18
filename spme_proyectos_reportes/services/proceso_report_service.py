from .base_report_service import BaseReportService

class ProcesoReportService(BaseReportService):
    def __init__(self, proceso):
        super().__init__()
        self.proceso = proceso

    def build_section(self, doc=None):
        target = doc or self.doc
        target.add_heading(f"Proceso: {self.proceso.codigo}", level=5)
        target.add_paragraph(f"{self.proceso.titulo}")
        target.add_paragraph(self.proceso.descripcion)

        if not doc:
            filename = f"reporte_proceso_{self.proceso.codigo}.docx"
            self.save(filename)
            return filename

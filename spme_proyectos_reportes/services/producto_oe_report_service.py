from .base_report_service import BaseReportService
from .proceso_report_service import ProcesoReportService

class ProductoOEReportService(BaseReportService):
    def __init__(self, producto):
        super().__init__()
        self.p = producto

    def build_section(self, doc=None):
        target = doc or self.doc

        target.add_heading(f"Producto OE {self.p.codigo}", level=4)
        target.add_paragraph(self.p.descripcion)

        # Procesos asociados
        procesos = self.p.proceso_producto_oe.all()
        if procesos.exists():
            target.add_heading("Procesos del Producto OE", level=5)
            for pr in procesos:
                pr_service = ProcesoReportService(pr)
                pr_service.build_section(target)

        if not doc:
            filename = f"reporte_producto_oe_{self.p.codigo}.docx"
            self.save(filename)
            return filename

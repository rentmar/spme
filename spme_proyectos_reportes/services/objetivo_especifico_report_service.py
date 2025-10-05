from .base_report_service import BaseReportService
from .resultado_oe_report_service import ResultadoOEReportService
from .producto_oe_report_service import ProductoOEReportService

class ObjetivoEspecificoReportService(BaseReportService):
    def __init__(self, objetivo):
        super().__init__()
        self.oe = objetivo

    def build_section(self, doc=None):
        target = doc or self.doc

        target.add_heading(f"Objetivo Específico {self.oe.codigo}", level=3)
        target.add_paragraph(self.oe.descripcion)

        # Indicadores
        indicadores = self.oe.indicador_oe.all()
        if indicadores.exists():
            target.add_heading("Indicadores del Objetivo Específico", level=4)
            for ind in indicadores:
                target.add_paragraph(f"• {ind.codigo}: {ind.descripcion}")

        # Resultados OE
        resultados = self.oe.resultados_oe.all()
        if resultados.exists():
            target.add_heading("Resultados del Objetivo Específico", level=4)
            for r in resultados:
                roe_service = ResultadoOEReportService(r)
                roe_service.build_section(target)

        # Productos OE
        productos = self.oe.productos_oe.all()
        if productos.exists():
            target.add_heading("Productos del Objetivo Específico", level=4)
            for p in productos:
                poe_service = ProductoOEReportService(p)
                poe_service.build_section(target)

        if not doc:
            filename = f"reporte_oe_{self.oe.codigo}.docx"
            self.save(filename)
            return filename

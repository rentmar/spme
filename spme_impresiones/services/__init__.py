from .pdf_base import BasePDFGenerator
from .pdf_factory import PDFGeneratorFactory
from .solicitud_fondos_pdf import SolicitudFondosPDFGenerator
from .solicitud_reembolso_pdf import SolicitudReembolsoPDFGenerator

# Para uso directo
PDFGeneratorService = PDFGeneratorFactory
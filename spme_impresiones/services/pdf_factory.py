from .solicitud_fondos_pdf import SolicitudFondosPDFGenerator
from .solicitud_reembolso_pdf import SolicitudReembolsoPDFGenerator
from .solicitud_viaje_pdf import SolicitudViajePDFGenerator
from .solicitud_pago_directo_pdf import SolicitudPagoDirectoPDFGenerator
from .rendicion_cuentas_pdf import RendicionCuentasPDFGenerator
from .solicitud_fondos_tarea_pdf import SolicitudFondosTareaPDFGenerator
# Importa los otros generadores cuando los crees

class PDFGeneratorFactory:
    """
    Fábrica para crear generadores de PDF según el tipo de objeto
    """
    
    GENERATORS = {
        'SolicitudFondos': SolicitudFondosPDFGenerator,
        'SolicitudFondosTarea': SolicitudFondosTareaPDFGenerator,
        'SolicitudViaje': SolicitudViajePDFGenerator,
        'SolicitudReembolso': SolicitudReembolsoPDFGenerator,
        'SolicitudPagoDirecto': SolicitudPagoDirectoPDFGenerator,
        'RendicionCuentas': RendicionCuentasPDFGenerator, 
        # Agrega los otros tipos aquí
    }
    
    @classmethod
    def get_generator(cls, obj):
        """
        Retorna el generador apropiado para el objeto
        """
        model_name = obj.__class__.__name__
        
        if model_name in cls.GENERATORS:
            return cls.GENERATORS[model_name]()
        else:
            raise ValueError(f"No hay generador de PDF definido para {model_name}")
    
    @classmethod
    def generate_pdf(cls, obj):
        """
        Método de conveniencia para generar PDF directamente
        """
        generator = cls.get_generator(obj)
        return generator.generate(obj)
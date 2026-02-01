from .solicitud_fondos_pdf import SolicitudFondosPDFGenerator
from .solicitud_reembolso_pdf import SolicitudReembolsoPDFGenerator
# Importa los otros generadores cuando los crees

class PDFGeneratorFactory:
    """
    Fábrica para crear generadores de PDF según el tipo de objeto
    """
    
    GENERATORS = {
        'SolicitudFondos': SolicitudFondosPDFGenerator,
        'SolicitudReembolso': SolicitudReembolsoPDFGenerator,
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
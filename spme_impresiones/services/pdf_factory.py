#pdf_factory
from .solicitud_fondos_pdf import SolicitudFondosPDFGenerator
from .solicitud_reembolso_pdf import SolicitudReembolsoPDFGenerator
from .solicitud_viaje_pdf import SolicitudViajePDFGenerator
from .solicitud_pago_directo_pdf import SolicitudPagoDirectoPDFGenerator
from .rendicion_cuentas_pdf import RendicionCuentasPDFGenerator
from .solicitud_fondos_tarea_pdf import SolicitudFondosTareaPDFGenerator
from .solicitud_reembolso_tarea_pdf import SolicitudReembolsoTareaPDFGenerator
from .solicitud_viaje_tarea_pdf import SolicitudViajeTareaPDFGenerator
from .solicitud_pago_directo_tarea_pdf import SolicitudPagoDirectoTareaPDFGenerator
from .rendicion_cuentas_tarea_pdf import RendicionCuentasTareaPDFGenerator
from .solicitud_fondos_act_pei_pdf import SolicitudFondosActPeiPDFGenerator
from .solicitud_fondos_tarea_pei_pdf import SolicitudFondosTareaPeiPDFGenerator

# Importa los otros generadores cuando los crees

class PDFGeneratorFactory:
    """
    Fábrica para crear generadores de PDF según el tipo de objeto
    """
    
    GENERATORS = {
        'SolicitudFondos': SolicitudFondosPDFGenerator,
        'SolicitudFondosTarea': SolicitudFondosTareaPDFGenerator,
        'SolicitudViaje': SolicitudViajePDFGenerator,
        'SolicitudViajeTarea': SolicitudViajeTareaPDFGenerator,
        'SolicitudReembolso': SolicitudReembolsoPDFGenerator,
        'SolicitudReembolsoTarea': SolicitudReembolsoTareaPDFGenerator, 
        'SolicitudPagoDirecto': SolicitudPagoDirectoPDFGenerator,
        'SolicitudPagoDirectoTarea': SolicitudPagoDirectoTareaPDFGenerator,
        'RendicionCuentas': RendicionCuentasPDFGenerator, 
        'RendicionCuentasTarea': RendicionCuentasTareaPDFGenerator,
        'SolicitudFondosActPei': SolicitudFondosActPeiPDFGenerator,
        'SolicitudFondosTareaPei': SolicitudFondosTareaPeiPDFGenerator, 
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
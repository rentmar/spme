# pdf_factory.py
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
from .solicitud_viaje_act_pei_pdf import SolicitudViajeActPeiPDFGenerator
from .solicitud_viaje_tarea_pei_pdf import SolicitudViajeTareaPeiPDFGenerator
from .solicitud_pago_directo_act_pei_pdf import SolicitudPagoDirectoActPeiPDFGenerator
from .solicitud_pago_directo_tarea_pei_pdf import SolicitudPagoDirectoTareaPeiPDFGenerator
from .solicitud_reembolso_act_pei_pdf import SolicitudReembolsoActPeiPDFGenerator
from .solicitud_reembolso_tarea_pei_pdf import SolicitudReembolsoTareaPeiPDFGenerator
from .rendicion_cuentas_act_pei_pdf import RendicionCuentasActPeiPDFGenerator
from .rendicion_cuentas_tarea_pei_pdf import RendicionCuentasTareaPeiPDFGenerator

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
        'SolicitudViajeActPei': SolicitudViajeActPeiPDFGenerator, 
        'SolicitudViajeActPeiTarea': SolicitudViajeTareaPeiPDFGenerator,
        'SolicitudPagoDirectoActPei': SolicitudPagoDirectoActPeiPDFGenerator,
        'SolicitudPagoDirectoTareaPei': SolicitudPagoDirectoTareaPeiPDFGenerator,
        'SolicitudReembolsoActPei': SolicitudReembolsoActPeiPDFGenerator,
        'SolicitudReembolsoTareaPei': SolicitudReembolsoTareaPeiPDFGenerator, 
        'RendicionCuentasActPei': RendicionCuentasActPeiPDFGenerator,
        'RendicionCuentasTareaPei': RendicionCuentasTareaPeiPDFGenerator,
    }
    
    @classmethod
    def get_generator(cls, obj):
        """
        Retorna el generador apropiado para el objeto
        """
        model_name = obj.__class__.__name__
        
        # CASOS ESPECIALES: Modelos que tienen versión actividad/tarea
        if model_name == 'SolicitudPagoDirectoActPei':
            if obj.tarea:
                return cls.GENERATORS['SolicitudPagoDirectoTareaPei']()
            else:
                return cls.GENERATORS['SolicitudPagoDirectoActPei']()
        
        elif model_name == 'SolicitudFondosActPei':
            if obj.tarea:
                return cls.GENERATORS['SolicitudFondosTareaPei']()
            else:
                return cls.GENERATORS['SolicitudFondosActPei']()
        
        elif model_name == 'SolicitudViajeActPei':
            if obj.tarea:
                return cls.GENERATORS['SolicitudViajeTareaPei']()
            else:
                return cls.GENERATORS['SolicitudViajeActPei']()
        
        #Reembolso
        elif model_name == 'SolicitudReembolsoActPei':
            if obj.tarea:
                return cls.GENERATORS['SolicitudReembolsoTareaPei']()
            else:
                return cls.GENERATORS['SolicitudReembolsoActPei']()

        elif model_name == 'RendicionCuentasActPei':
            if obj.tarea:
                # rendición de tarea
                # return cls.GENERATORS['RendicionCuentasTareaPei']()
                return cls.GENERATORS['RendicionCuentasTareaPei']()
            else:
                return cls.GENERATORS['RendicionCuentasActPei']()    
        
        # Para modelos sin versión actividad/tarea
        if model_name in cls.GENERATORS:
            return cls.GENERATORS[model_name]()
        
        raise ValueError(f"No hay generador de PDF definido para {model_name}")    
    
    @classmethod
    def generate_pdf(cls, obj):
        """
        Método de conveniencia para generar PDF directamente
        """
        generator = cls.get_generator(obj)
        return generator.generate(obj)
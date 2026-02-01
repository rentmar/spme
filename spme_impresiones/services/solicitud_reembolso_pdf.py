from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import SolicitudReembolso

class SolicitudReembolsoPDFGenerator(BasePDFGenerator):
    """
    Generador específico para Solicitud de Reembolso
    """
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/solicitud_reembolso_template.html'
    
    def prepare_context(self, obj):
        """
        Prepara el contexto específico para Solicitud de Reembolso
        """
        if not isinstance(obj, SolicitudReembolso):
            raise ValueError("El objeto debe ser una instancia de SolicitudReembolso")
        
        context = {
            'numero_formulario': obj.numeroFormulario or "No asignado",
            'fecha_emision': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'codigo_actividad': obj.actividad.codigo if obj.actividad else "No asignado",
            'nombre_solicitante': obj.get_nombre_completo_solicitante(),
            'documento_identidad': obj.get_documento_identidad(),
            'cargo': obj.get_cargo(),
            'nombre_actividad': obj.actividad.nombreCorto if obj.actividad else "No especificado",
            'fecha_ejecucion': obj.fechaRealizacionActividad.strftime('%d/%m/%Y') if obj.fechaRealizacionActividad else "No especificada",
            'descripcion_actividad': obj.descripcion_actividad or "No especificada",
            'objetivo_actividad': obj.objetivo_actividad or "No especificado",
            'lugar_solicitud': obj.lugarSolicitud or "No especificado",
            'fecha_solicitud': obj.fechaSolicitud.strftime('%d/%m/%Y') if obj.fechaSolicitud else "No especificada",
            'forma_pago': obj.formaPago.formaPago if obj.formaPago else "No especificada",
            'total_monto_solicitado': float(obj.montoSolicitado) if obj.montoSolicitado else 0.00,
            'tipo_documento': 'SOLICITUD DE REEMBOLSO',
            'subtipo_documento': 'F-02',
        }
        
        # Procesar detalle de gastos
        detalle_gastos = []
        if obj.detalleDestinoFondos:
            for item in obj.detalleDestinoFondos:
                detalle_gastos.append({
                    'partida': item.get('partida', '-'),
                    'descripcion_gasto': item.get('descripcionGasto', '-'),
                    'monto': float(item.get('monto', 0)),
                    'observaciones': item.get('observaciones', '-')
                })
        context['detalle_gastos'] = detalle_gastos
        
        return context
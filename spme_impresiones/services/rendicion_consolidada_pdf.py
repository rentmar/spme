# spme/spme_impresiones/services/rendicion_consolidada_pdf.py
# spme/spme_impresiones/services/rendicion_consolidada_pdf.py
import os
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from pypdf import PdfWriter, PdfReader
from .pdf_base import BasePDFGenerator
from spme_monitoreo.models import RendicionCuentas
from decimal import Decimal
from collections import defaultdict
#Validaciones 
from .validadores_documentos_service import ValidadoresDocumentoService



class RendicionConsolidadaPDFGenerator(BasePDFGenerator):
    """
    Generador para la Rendición de Cuentas Consolidada.
    Renderiza cada sección como un documento PDF independiente y los fusiona 
    con pypdf (PdfWriter) para asegurar paginación aislada ('Página 1 de 1').
    """

    USAR_ETIQUETAS_GENERICAS = True
    
    def __init__(self):
        super().__init__()
        self.template_name = 'spme_impresiones/rendicion_consolidada_template.html'
        self.validacion_service = ValidadoresDocumentoService()
        # Agrega este diccionario de etiquetas de revisores aquí:
        self.etiquetas_revisor = {
            'admin': 'REVISOR',
            'coordinador': 'REVISOR',
            'tecnico': 'REVISOR',
            'contable': 'REVISOR',
            'dir-administrativo': 'REVISOR',
        }
    
    def prepare_context(self, obj):
        #Comprobacion, si es una instancia valida
        if not isinstance(obj, RendicionCuentas):
            raise ValueError("El objeto debe ser una instancia de RendicionCuentas")

        #Extraer el numero de la rendicion de cuentas
        num_form = obj.numeroFormulario or f"RC_{obj.id}"
        
        # Obtenemos el contexto base definido en el modelo
        base_context = obj.get_mensaje_contexto()

        print(base_context)

        #Datos del solicitante/responsable
        solicitante_obj = obj.usuario or obj.responsable
        solicitante_nombre = (
            solicitante_obj.get_full_name()
            if solicitante_obj and hasattr(solicitante_obj, 'get_full_name') and solicitante_obj.get_full_name() 
            else (str(solicitante_obj) if solicitante_obj else "No asignado")
        )

        #Formatear cantidades para los descargos
        monto_asig = float(base_context.get('monto') or 0)
        monto_desc = float(base_context.get('monto_descargado') or 0)
        saldo_val = float(base_context.get('saldo') or 0)

        # Obtener contexto completo de validación y estado consolidado a través del servicio
        if self.USAR_ETIQUETAS_GENERICAS:
            contexto_validacion = self.validacion_service.preparar_contexto_rendicion_pdf(obj, self.etiquetas_revisor)
        else:
            contexto_validacion = self.validacion_service.preparar_contexto_rendicion_pdf(obj)

        # Filtrar la lista de validadores para excluir al 'coordinador' de la visualización de firmas
        validadores_filtrados = [
            v for v in contexto_validacion['validadores'] 
            if v.get('cargo', '').lower() != 'coordinador'
        ]

        # =========================================================================
        # PROCESAMIENTO Y AGRUPACIÓN DE DESGLOSES DE FONDOS POR HOJA (NUEVO)
        # =========================================================================
        datos_fondos_original = base_context.get('datos_vinculacion_fondos') or {}
        detalle_descargado_fondos = datos_fondos_original.get('detalle_descargado', [])

        hojas_dict = defaultdict(lambda: {'hoja_id': None, 'hoja_titulo': '', 'items': [], 'total': Decimal('0.00')})

        for item in detalle_descargado_fondos:
            h_id = item.get('hoja_id', 1)
            h_titulo = item.get('hoja_titulo', 'Detalle de Gastos')
            
            hojas_dict[h_id]['hoja_id'] = h_id
            hojas_dict[h_id]['hoja_titulo'] = h_titulo
            hojas_dict[h_id]['items'].append(item)
            hojas_dict[h_id]['total'] += Decimal(str(item.get('monto', 0) or 0))

        # Convertir el diccionario agrupado en una lista ordenada para la plantilla
        lista_hojas_desglose = list(hojas_dict.values())
        
        # Inyectar la estructura de hojas procesadas dentro del diccionario de datos de fondos
        datos_fondos_procesados = {
            **datos_fondos_original,
            'hojas_desglose': lista_hojas_desglose
        }



        contexto = {
            **base_context,
            #Informacion base
            'numero_formulario': num_form,
            'tipo_documento': 'RENDICIÓN DE CUENTAS',
            'subtipo_documento': f"Tipo: {base_context.get('subtipo_display')}",
            'fecha_emision': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada",
            #Datos para la seccion informacion general
            'rendicion':{
                'id': obj.id,
                'numero_formulario': num_form,
                'fecha_rendicion': obj.fechaRendicion.strftime('%d/%m/%Y') if obj.fechaRendicion else "No especificada",
                'lugar_rendicion': obj.lugarRendicion or "No especificado",
            },
            #Datos para la seccion responsable
            'responsable':{
                'nombre': solicitante_nombre,
                'documento_identidad': getattr(solicitante_obj, 'documentoIdentidad', None) or getattr(solicitante_obj, 'ci', '-') if solicitante_obj else '-',
                'cargo': getattr(solicitante_obj, 'cargo', '-') if solicitante_obj else '-',
            },

            #Datos para la seccion actividad y origen
            'actividad_origen':{
                'actividad_codigo': base_context.get('codigo_actividad') or "Sin codigo",
                'actividad_nombre': base_context.get('actividad_nombre') or 'Sin Nombre',
                'descripcion_actividad': base_context.get('descripcion_actividad') or 'S/D',
                'lugar_actividad': base_context.get('lugar_actividad') or '',
                'fecha_actividad': base_context.get('fecha_actividad') or '-',
                'fecha_inicio': base_context.get('fecha_inicio') or '-',
                'fecha_fin': base_context.get('fecha_fin') or '-',
            },

            #Datos para la seccion resumen financiero
            'resumen_financiero': {
                'monto_asignado': f"{monto_asig:.2f}",
                'monto_descargado': f"{monto_desc:.2f}",
                'saldo': f"{saldo_val:.2f}",
                'tiene_saldo_favor': saldo_val < 0,
                'tiene_saldo_debito': saldo_val > 0,
            },

            #Datos para la seccion detalle de gastos
            'detalle_gastos': obj.get_items_para_impresion(),

            # Variables inyectadas para la sección de Firmas y Validaciones
            'validadores': validadores_filtrados,
            'solicitante': contexto_validacion['solicitante'],
            'estado_documento': contexto_validacion['estado_documento'],
            'total_validadores': contexto_validacion['total_validadores'],
            'aprobados': contexto_validacion['aprobados'],
            'pendientes': contexto_validacion['pendientes'],
            'rechazados': contexto_validacion['rechazados'],

            #Control de Secciones Activas
            'doc_rendicion_general': {
                'activo': True,
            },
            'doc_solicitud_fondos': {
                'activo': base_context.get('tiene_vinculacion_fondos', False),
                'datos': datos_fondos_procesados
            },
            'doc_solicitud_viaje': {
                'activo': base_context.get('tiene_vinculacion_viaje', False),
                'datos': base_context.get('datos_vinculacion_viaje') or {}
            },

            'datos_vinculacion_fondos': datos_fondos_procesados,
            
            # Aquí iremos agregando los diccionarios de cada sección uno por uno
            
        }
            
        return contexto

    def generate_filename(self, obj):
        if self.filename:
            return self.filename
        numero_limpio = (obj.numeroFormulario or f"RC_{obj.id}").replace('/', '_').replace('\\', '_')
        return f"Rendicion_Consolidada_{numero_limpio}.pdf"

    def render_to_pdf(self, template_name, context):
        full_context = {**self.get_common_context(), **context}
        font_config = FontConfiguration()
        temp_files = []
        
        try:
            writer = PdfWriter()
            num_form = context.get('numero_formulario', 'S/N')

            # 1. FORMULARIO COMPLETO: Rendición de Cuentas General
            if context.get('doc_rendicion_general', {}).get('activo'):
                ctx_rendicion = {
                    **full_context, 
                    'numero_formulario': num_form,
                    'documento_activo': 'rendicion_general',
                    'tipo_documento': 'RENDICIÓN DE CUENTAS',
                    'subtipo_documento': f'N° {num_form}',
                }
                html_str = render_to_string(template_name, ctx_rendicion)
                
                tmp_rendicion = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_files.append(tmp_rendicion.name)
                tmp_rendicion.close()
                
                HTML(string=html_str, base_url=settings.BASE_DIR).write_pdf(tmp_rendicion.name, font_config=font_config)
                writer.append(PdfReader(tmp_rendicion.name, 'rb'))

            #2. Documento adicional: SOlicitud de fondos vinculado
            doc_fondos = context.get('doc_solicitud_fondos', {})
            if doc_fondos.get('activo'):
                ctx_fondos = {
                    **full_context,
                    'numero_formulario': num_form,
                    'documento_activo': 'solicitud_fondos', # Identificador para la plantilla HTML
                    'tipo_documento': 'RENDICION DE CUENTAS - SOLICITUD DE FONDOS',
                    'subtipo_documento': f"Ref. Rendición: {num_form}",
                    'info_general_solicitud': {
                        'numero_formulario': num_form,
                        'fecha_solicitud': context.get('fecha_solicitud', '-'),
                        'lugar_solicitud': context.get('lugar_rendicion', '-'),
                    }
                }
                html_str_fondos = render_to_string(template_name, ctx_fondos)

                tmp_fondos = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_files.append(tmp_fondos.name)
                tmp_fondos.close()

                HTML(string=html_str_fondos, base_url=settings.BASE_DIR).write_pdf(tmp_fondos.name, font_config=font_config)
                writer.append(PdfReader(tmp_fondos.name, 'rb'))

            #3. DOCUMENTO ADICIONAL: Solicitude de viajes vinculada
            doc_viaje = context.get('doc_solicitud_viaje', {})
            if doc_viaje.get('activo'):
                ctx_viaje = {
                    **full_context,
                    'numero_formulario': num_form,
                    'documento_activo': 'solicitud_viaje', # Identificador para la plantilla HTML
                }
                html_str_viaje = render_to_string(template_name, ctx_viaje)

                tmp_viaje = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_files.append(tmp_viaje.name)
                tmp_viaje.close()

                HTML(string=html_str_viaje, base_url=settings.BASE_DIR).write_pdf(tmp_viaje.name, font_config=font_config)
                writer.append(PdfReader(tmp_viaje.name, 'rb'))

            final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_files.append(final_tmp.name)
            final_tmp.close()
            
            with open(final_tmp.name, 'wb') as output_file:
                writer.write(output_file)
            
            writer.close()

            with open(final_tmp.name, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            return pdf_content

        except Exception as e:
            print(f"Error generando PDF consolidado: {str(e)}")
            raise
        finally:
            for path in temp_files:
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except Exception:
                        pass
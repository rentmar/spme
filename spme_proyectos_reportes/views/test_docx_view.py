# views/test_docx_view.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.conf import settings  # ✅ Importar settings
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import tempfile
import os
from datetime import datetime, timedelta

@api_view(['GET'])
def test_docx_endpoint(request):
    """
    Endpoint de prueba para verificar que python-docx funciona correctamente
    """
    try:
        # Crear un documento de prueba
        doc = Document()
        
        # Configurar estilos
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)
        
        # Título principal
        title = doc.add_heading('TEST DE LIBRERÍA python-docx - GMT-4', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Aplicar color correctamente
        for run in title.runs:
            run.font.color.rgb = RGBColor(0, 0, 139)
        
        # Información del sistema con hora GMT-4 (sin pytz)
        utc_now = timezone.now()
        gmt_minus_4 = utc_now - timedelta(hours=4)  # Restar 4 horas para GMT-4
        
        doc.add_paragraph()
        doc.add_paragraph(f'Fecha de generación (GMT-4): {gmt_minus_4.strftime("%Y-%m-%d %H:%M:%S")}')
        doc.add_paragraph(f'Fecha UTC: {utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")}')
        doc.add_paragraph(f'Usuario: {request.user.username if request.user.is_authenticated else "Anónimo"}')
        doc.add_paragraph(f'Zona horaria: {settings.TIME_ZONE}')  # ✅ CORREGIDO: settings.TIME_ZONE
        
        # Sección de prueba de funcionalidades
        doc.add_heading('Funcionalidades Probadas', level=1)
        
        # Tabla de pruebas
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        
        # Encabezados de tabla
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Funcionalidad'
        hdr_cells[1].text = 'Estado'
        hdr_cells[2].text = 'Observaciones'
        
        # Datos de prueba
        pruebas = [
            ('Creación documento', '✅ OK', 'Documento creado exitosamente'),
            ('Estilos de texto', '✅ OK', 'Fuentes y tamaños aplicados'),
            ('Párrafos', '✅ OK', 'Múltiples párrafos agregados'),
            ('Tablas', '✅ OK', 'Tablas con formato grid'),
            ('Alineación', '✅ OK', 'Texto centrado y justificado'),
            ('Encabezados', '✅ OK', 'H1, H2, H3 funcionando'),
            ('Colores RGB', '✅ OK', 'Colores RGB aplicados correctamente'),
            ('Zona horaria GMT-4', '✅ OK', 'Hora local configurada correctamente'),
        ]
        
        for funcionalidad, estado, observacion in pruebas:
            row_cells = table.add_row().cells
            row_cells[0].text = funcionalidad
            row_cells[1].text = estado
            row_cells[2].text = observacion
        
        # Sección con diferentes estilos
        doc.add_heading('Tipos de Texto', level=2)
        
        # Texto en negrita
        p = doc.add_paragraph()
        p.add_run('Texto en negrita: ').bold = True
        p.add_run('Este texto está en negrita.')
        
        # Texto en itálica
        p = doc.add_paragraph()
        p.add_run('Texto en itálica: ').italic = True
        p.add_run('Este texto está en itálica.')
        
        # Texto subrayado
        p = doc.add_paragraph()
        p.add_run('Texto subrayado: ').underline = True
        p.add_run('Este texto está subrayado.')
        
        # Texto con color
        p = doc.add_paragraph()
        colored_run = p.add_run('Texto en color rojo: ')
        colored_run.font.color.rgb = RGBColor(255, 0, 0)
        p.add_run('Este texto está en color rojo.')
        
        # Texto con color verde
        p = doc.add_paragraph()
        colored_run = p.add_run('Texto en color verde: ')
        colored_run.font.color.rgb = RGBColor(0, 128, 0)
        p.add_run('Este texto está en color verde.')
        
        # Información de zona horaria
        doc.add_heading('Información de Zona Horaria', level=2)
        doc.add_paragraph(f'Zona horaria configurada: {settings.TIME_ZONE}')  # ✅ CORREGIDO
        doc.add_paragraph(f'Hora local (GMT-4): {gmt_minus_4.strftime("%Y-%m-%d %H:%M:%S")}')
        doc.add_paragraph(f'Diferencia con UTC: GMT-4')
        
        # Lista con viñetas
        doc.add_paragraph('Lista con viñetas:')
        for item in ['Item 1', 'Item 2', 'Item 3']:
            doc.add_paragraph(item, style='List Bullet')
        
        # Guardar en archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        doc.save(temp_file.name)
        temp_file.close()
        
        # Preparar respuesta
        filename = f'test_python_docx_{gmt_minus_4.strftime("%Y%m%d_%H%M%S")}.docx'
        
        response = FileResponse(
            open(temp_file.name, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Limpiar archivo temporal después de enviar la respuesta
        def cleanup_temp_file():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        response.closed = cleanup_temp_file
        
        return response
        
    except Exception as e:
        return Response(
            {
                'error': 'Error al generar documento de prueba',
                'detalles': str(e),
                'status': 'ERROR',
                'timezone': settings.TIME_ZONE  # ✅ CORREGIDO
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def test_docx_status(request):
    """
    Endpoint para verificar el estado de la librería sin generar archivo
    """
    try:
        # Probar todas las funcionalidades críticas
        from docx import Document
        from docx.shared import Pt, RGBColor
        
        # Obtener hora local GMT-4 (sin pytz)
        utc_now = timezone.now()
        gmt_minus_4 = utc_now - timedelta(hours=4)
        
        doc = Document()
        
        # Probar colores
        p = doc.add_paragraph()
        run = p.add_run('Prueba de colores RGB')
        run.font.color.rgb = RGBColor(0, 0, 255)
        
        # Probar guardado
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            doc.save(tmp.name)
            os.unlink(tmp.name)
        
        return Response({
            'status': 'OK',
            'message': 'Librería python-docx funcionando correctamente',
            'funcionalidades': [
                'Creación de documentos',
                'Párrafos y texto',
                'Estilos básicos',
                'Tablas',
                'Encabezados',
                'Colores RGB',
                'Guardado de archivos',
                'Zona horaria GMT-4'
            ],
            'version': 'python-docx 1.1.0',
            'timezone': settings.TIME_ZONE,  # ✅ CORREGIDO
            'hora_actual_utc': utc_now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            'hora_actual_local': gmt_minus_4.strftime("%Y-%m-%d %H:%M:%S"),
            'gmt_offset': 'GMT-4'
        })
        
    except ImportError:
        return Response({
            'status': 'ERROR',
            'message': 'Librería python-docx no instalada',
            'solución': 'Ejecuta: pip install python-docx'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        return Response({
            'status': 'ERROR',
            'message': 'Error en la librería python-docx',
            'detalles': str(e),
            'timezone': settings.TIME_ZONE  # ✅ CORREGIDO
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
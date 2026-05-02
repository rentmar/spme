#services/generators/pei_generator.py
from django.utils import timezone
from ...utils.word_styles import ESTILOS_PEI

class PEIGenerator:
    """Genera la sección del PEI en el documento Word."""
    def generate(self, base_doc, nodo: dict, nivel: int):
        doc = base_doc.document
        datos = nodo['datos']

        base_doc.agregar_parrafo_estilo("REPORTE PEI", ESTILOS_PEI['TITULO_PRINCIPAL'])
        base_doc.agregar_parrafo_estilo(datos.get('titulo', ''), ESTILOS_PEI['TITULO_PRINCIPAL'])

        fecha = timezone.now().strftime('%d/%m/%Y %H:%M')
        base_doc.agregar_parrafo_estilo(f"Generado: {fecha}", ESTILOS_PEI['METADATO'])

        doc.add_paragraph()
        doc.add_heading('INFORMACIÓN GENERAL DEL PEI', level=1)

        campos = [
            ('Título', datos.get('titulo', '')),
            ('Descripción', datos.get('descripcion', '')),
            ('Fecha Inicio', str(datos.get('fecha_inicio', ''))),
            ('Fecha Fin', str(datos.get('fecha_fin', ''))),
            ('Vigente', 'Sí' if datos.get('esta_vigente') else 'No'),
        ]

        tabla = base_doc.crear_tabla_formato(len(campos), 2)
        for i, (campo, valor) in enumerate(campos):
            tabla.cell(i, 0).text = campo
            tabla.cell(i, 1).text = str(valor if valor else '')
            for p in tabla.cell(i, 0).paragraphs:
                for r in p.runs:
                    r.bold = True
                    
        doc.add_paragraph()
        base_doc.agregar_separador()
        doc.add_paragraph()
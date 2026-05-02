#services/generators/objetivo_generator.py
class ObjetivoGenerator:
    """Genera la sección de un objetivo en el documento Word."""
    def generate(self, base_doc, nodo: dict, nivel: int):
        doc = base_doc.document
        datos = nodo['datos']

        if nivel == 0:
            doc.add_heading('REPORTE DE OBJETIVO', level=1)
        
        codigo = datos.get('codigo', '')
        titulo = f"OBJETIVO: {codigo}" if codigo else "OBJETIVO"
        doc.add_heading(titulo, level=2)
        
        campos = [
            ('Código', codigo),
            ('Descripción', datos.get('descripcion', '')),
            ('PEI', datos.get('pei_titulo', '')),
        ]
        tabla = base_doc.crear_tabla_formato(len(campos), 2)
        for i, (campo, valor) in enumerate(campos):
            tabla.cell(i, 0).text = campo
            tabla.cell(i, 1).text = str(valor if valor else '')
            for p in tabla.cell(i, 0).paragraphs:
                for r in p.runs:
                    r.bold = True
                    
        doc.add_paragraph()
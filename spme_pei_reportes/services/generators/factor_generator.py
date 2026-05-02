# services/generators/factor_generator.py

class FactorGenerator:
    """Genera la sección de factores críticos en el documento Word."""
    
    def generate(self, base_doc, nodo: dict, nivel: int):
        doc = base_doc.document
        datos = nodo['datos']
        
        if nivel == 0:
            doc.add_heading('FACTOR CRÍTICO', level=1)
            doc.add_paragraph(datos.get('factor_critico', ''))
            if datos.get('objetivo_codigo'):
                doc.add_paragraph(f"Objetivo asociado: {datos.get('objetivo_codigo')}")
        else:
            doc.add_heading('FACTORES CRÍTICOS', level=3)
            texto = datos.get('factor_critico', '')
            if texto:
                doc.add_paragraph(texto, style='List Bullet')
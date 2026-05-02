# services/generators/indicador_base_generator.py
class IndicadorBaseGenerator:
    """Genera UNA tabla por indicador con todos sus campos."""
    
    def generate(self, base_doc, nodo: dict, nivel: int):
        doc = base_doc.document
        datos = nodo['datos']
        
        # Encabezado
        codigo = datos.get('codigo', '')
        titulo = f"INDICADOR: {codigo}" if codigo else "INDICADOR"
        doc.add_heading(titulo, level=3)
        
        # Construir lista de campos (comunes + específicos)
        campos = self._obtener_campos_comunes(datos)
        campos.extend(self._obtener_campos_especificos(datos))
        
        # Una sola tabla con todos los campos
        tabla = base_doc.crear_tabla_formato(len(campos), 2)
        for i, (campo, valor) in enumerate(campos):
            tabla.cell(i, 0).text = campo
            tabla.cell(i, 1).text = str(valor if valor else '')
            for p in tabla.cell(i, 0).paragraphs:
                for r in p.runs:
                    r.bold = True
        
        doc.add_paragraph()
    
    def _obtener_campos_comunes(self, datos: dict) -> list:
        """Campos base de cualquier indicador."""
        return [
            ('Código', datos.get('codigo', '')),
            ('Tipo', datos.get('tipo_medicion', '')),
            ('Descripción', datos.get('descripcion', '')),
            ('Captura de Información', datos.get('captura_informacion', '')),
            ('Responsabilidad', datos.get('responsabilidad', '')),
            ('Frecuencia de Recopilación', datos.get('frecuencia_recopilacion', '')),
            ('Uso de Información', datos.get('uso_informacion', '')),
        ]
    
    def _obtener_campos_especificos(self, datos: dict) -> list:
        """Sobrescribir en subclases. Retorna lista de tuplas (campo, valor)."""
        return []
"""
ReportContext: Estado global del documento Word durante la generación.
Maneja el documento, numeración, estilos y formateo.
No conoce el árbol ni los renderers.
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime, date
from decimal import Decimal


class ReportContext:
    """
    Mantiene el documento Word y el estado de generación.
    
    Responsabilidades:
    - Crear y mantener el documento python-docx
    - Numeración automática de secciones (1, 1.1, 1.1.1, ...)
    - Agregar elementos: headings, párrafos, tablas, saltos de página
    - Formateo de datos: fechas, montos, duraciones
    - Índice de contenidos
    - Numeración de páginas
    - Estilos base del documento
    """
    
    def __init__(self, config: dict):
        """
        Args:
            config: {
                'incluir_indice': bool,
                'modo_actividades': str,
                'estilo': str,
            }
        """
        self.documento = Document()
        self.config = config
        
        # Numeración automática por nivel (dinámico, sin límite)
        self._contadores = {}
        
        # Índice
        self._entradas_indice = []
        self._indice_activado = config.get('incluir_indice', False)
        
        # Actividades para anexo
        self.modo_actividades = config.get('modo_actividades', 'anexo')
        self._actividades_anexo = {}
        
        # Configurar estilos base
        self._configurar_estilos()
    
    # =====================================================================
    # NUMERACIÓN AUTOMÁTICA
    # =====================================================================
    
    def agregar_heading(self, texto: str, nivel: int):
        """
        Agrega un encabezado numerado.
        
        Nivel 1 → '1. TEXTO'
        Nivel 2 → '1.1 TEXTO'
        Nivel 3 → '1.1.1 TEXTO'
        Nivel 0 → 'TEXTO' (sin número, para títulos principales)
        """
        if nivel > 0:
            self._incrementar_nivel(nivel)
            numeracion = self._get_numeracion(nivel)
            heading_texto = f"{numeracion} {texto}" if numeracion else texto
        else:
            heading_texto = texto
        
        self.documento.add_heading(heading_texto, level=nivel)
        
        if self._indice_activado and nivel > 0:
            self._entradas_indice.append({
                'texto': heading_texto,
                'nivel': nivel,
            })
    
    def agregar_titulo(self, texto: str):
        """Agrega un título principal sin numeración (nivel 0)."""
        self.agregar_heading(texto, nivel=0)
    
    def _incrementar_nivel(self, nivel: int):
        """Incrementa el contador del nivel y resetea los inferiores."""
        if nivel not in self._contadores:
            self._contadores[nivel] = 0
        self._contadores[nivel] += 1
        
        # Resetear niveles inferiores
        for key in list(self._contadores.keys()):
            if key > nivel:
                self._contadores[key] = 0
    
    def _get_numeracion(self, nivel: int) -> str:
        """Construye el string de numeración: '1.2.3'."""
        partes = []
        for i in range(1, nivel + 1):
            if i in self._contadores and self._contadores[i] > 0:
                partes.append(str(self._contadores[i]))
        return '.'.join(partes)
    
    # =====================================================================
    # PÁRRAFOS
    # =====================================================================
    
    def agregar_parrafo(self, texto: str, bold: bool = False, italic: bool = False,
                        alineacion: str = None):
        """
        Agrega un párrafo simple.
        
        Args:
            texto: Contenido del párrafo
            bold: Si aplicar negrita
            italic: Si aplicar cursiva
            alineacion: 'left', 'center', 'right', 'justify'
        """
        p = self.documento.add_paragraph()
        run = p.add_run(str(texto) if texto else '')
        run.bold = bold
        run.italic = italic
        
        if alineacion == 'center':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alineacion == 'right':
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        elif alineacion == 'justify':
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        return p
    
    def agregar_parrafo_destacado(self, texto: str):
        """Agrega un párrafo en estilo cita destacada."""
        p = self.documento.add_paragraph()
        p.style = self.documento.styles['Intense Quote']
        p.add_run(str(texto) if texto else '')
        return p
    
    def agregar_viñeta(self, texto: str):
        """Agrega un ítem con viñeta."""
        return self.documento.add_paragraph(str(texto), style='List Bullet')
    
    def agregar_texto_vacio(self):
        """Agrega un párrafo vacío como espaciador."""
        self.documento.add_paragraph()
    
    # =====================================================================
    # TABLAS
    # =====================================================================
    
    def agregar_tabla_datos(self, filas: list, titulo: str = None):
        """
        Agrega una tabla de 2 columnas: etiqueta | valor.
        
        Args:
            filas: Lista de tuplas [('Etiqueta', 'Valor'), ...]
            titulo: Título opcional arriba de la tabla
        """
        if titulo:
            self.agregar_parrafo(titulo, bold=True)
        
        tabla = self.documento.add_table(
            rows=len(filas), 
            cols=2, 
            style='Light Grid Accent 1'
        )
        
        for i, (etiqueta, valor) in enumerate(filas):
            celda_etiqueta = tabla.cell(i, 0)
            celda_etiqueta.text = str(etiqueta)
            for paragraph in celda_etiqueta.paragraphs:
                for run in paragraph.runs:
                    run.bold = True
            
            celda_valor = tabla.cell(i, 1)
            celda_valor.text = str(valor) if valor is not None else 'No especificado'
        
        self.agregar_texto_vacio()
        return tabla
    
    def agregar_tabla(self, headers: list, filas: list, titulo: str = None):
        """
        Agrega una tabla genérica con headers.
        
        Args:
            headers: Lista de nombres de columna ['Col1', 'Col2', ...]
            filas: Lista de listas [['a', 'b'], ['c', 'd'], ...]
            titulo: Título opcional arriba de la tabla
        """
        if titulo:
            self.agregar_parrafo(titulo, bold=True)
        
        tabla = self.documento.add_table(
            rows=len(filas) + 1,
            cols=len(headers),
            style='Light Grid Accent 1'
        )
        
        for j, header in enumerate(headers):
            celda = tabla.cell(0, j)
            celda.text = str(header)
            for paragraph in celda.paragraphs:
                for run in paragraph.runs:
                    run.bold = True
        
        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                tabla.cell(i + 1, j).text = str(valor) if valor is not None else ''
        
        self.agregar_texto_vacio()
        return tabla
    
    # =====================================================================
    # SALTOS DE PÁGINA
    # =====================================================================
    
    def agregar_salto_pagina(self):
        """Agrega un salto de página."""
        self.documento.add_page_break()
    
    # =====================================================================
    # FORMATEO DE DATOS (estáticos)
    # =====================================================================
    
    @staticmethod
    def fmt_fecha(fecha_str) -> str:
        if not fecha_str:
            return 'No especificada'
        try:
            if isinstance(fecha_str, str):
                dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            elif isinstance(fecha_str, (date, datetime)):
                dt = fecha_str
            else:
                return str(fecha_str)
            return dt.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            return str(fecha_str)
    
    @staticmethod
    def fmt_monto(monto) -> str:
        if not monto:
            return 'Bs. 0.00'
        try:
            return f"Bs. {Decimal(str(monto)):,.2f}"
        except:
            return str(monto)
    
    @staticmethod
    def fmt_duracion(inicio, fin) -> str:
        if not inicio or not fin:
            return 'No especificada'
        try:
            if isinstance(inicio, str):
                inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
            if isinstance(fin, str):
                fin = datetime.strptime(fin, '%Y-%m-%d').date()
            delta = fin - inicio
            meses = delta.days // 30
            dias = delta.days % 30
            return f"{meses} mes(es) y {dias} día(s)" if meses else f"{delta.days} día(s)"
        except:
            return 'No especificada'
    
    @staticmethod
    def fmt_booleano(valor) -> str:
        if valor is None:
            return 'No especificado'
        return 'Sí' if valor else 'No'
    
    @staticmethod
    def fmt_lista(lista: list) -> str:
        if not lista:
            return 'Ninguno'
        return ', '.join(str(item) for item in lista)
    
    # =====================================================================
    # FINALIZACIÓN
    # =====================================================================
    
    def finalizar(self):
        if self._indice_activado:
            self._generar_indice()
        self._agregar_numeracion_paginas()
        return self.documento
    
    def _generar_indice(self):
        if not self._entradas_indice:
            return
        for i, paragraph in enumerate(self.documento.paragraphs):
            if 'ÍNDICE' in paragraph.text.upper():
                for entrada in self._entradas_indice:
                    indent = '    ' * (entrada['nivel'] - 1)
                    texto_indice = f"{indent}{entrada['texto']}"
                    self.documento.paragraphs[i].add_run(f"\n{texto_indice}")
                break
    
    def _agregar_numeracion_paginas(self):
        """Agrega número de página en el footer de cada sección."""
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        for section in self.documento.sections:
            footer = section.footer
            footer.is_linked_to_previous = False
            
            paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Texto "Página "
            run_texto = paragraph.add_run("Página ")
            
            # Campo PAGE
            run_page = paragraph.add_run()
            fldChar_begin = OxmlElement('w:fldChar')
            fldChar_begin.set(qn('w:fldCharType'), 'begin')
            run_page._r.append(fldChar_begin)
            
            instrText = OxmlElement('w:instrText')
            instrText.set(qn('xml:space'), 'preserve')
            instrText.text = ' PAGE '
            run_page._r.append(instrText)
            
            fldChar_end = OxmlElement('w:fldChar')
            fldChar_end.set(qn('w:fldCharType'), 'end')
            run_page._r.append(fldChar_end)
        
    def _configurar_estilos(self):
        style = self.documento.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        for section in self.documento.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(3.0)
            section.right_margin = Cm(2.5)
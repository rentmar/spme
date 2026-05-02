#utils/word_styles.py
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ESTILOS_PEI = {
    'TITULO_PRINCIPAL': {
        'font_name': 'Calibri', 'font_size': Pt(18), 'bold': True,
        'color': RGBColor(0x1F, 0x4E, 0x79),
        'alignment': WD_ALIGN_PARAGRAPH.CENTER, 'space_after': Pt(12),
    },
    'HEADING_1': {
        'font_name': 'Calibri', 'font_size': Pt(16), 'bold': True,
        'color': RGBColor(0x2E, 0x75, 0xB6),
        'space_before': Pt(18), 'space_after': Pt(6),
    },
    'HEADING_2': {
        'font_name': 'Calibri', 'font_size': Pt(14), 'bold': True,
        'color': RGBColor(0x44, 0x72, 0xC4),
        'space_before': Pt(12), 'space_after': Pt(4),
    },
    'HEADING_3': {
        'font_name': 'Calibri', 'font_size': Pt(12), 'bold': True,
        'color': RGBColor(0x5B, 0x9B, 0xD5),
        'space_before': Pt(8), 'space_after': Pt(4),
    },
    'TABLA_DATOS': {
        'style_name': 'Light Grid Accent 1',
        'font_name': 'Calibri', 'font_size': Pt(10),
    },
    'METADATO': {
        'font_name': 'Calibri', 'font_size': Pt(9),
        'color': RGBColor(0x80, 0x80, 0x80), 'italic': True,
    },
    'TEXTO_NORMAL': {
        'font_name': 'Calibri', 'font_size': Pt(11),
    },
}

PAGE_CONFIG = {
    'top_margin': Cm(2.5), 'bottom_margin': Cm(2.5),
    'left_margin': Cm(2.5), 'right_margin': Cm(2.5),
} 
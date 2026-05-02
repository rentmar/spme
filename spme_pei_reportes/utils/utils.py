#utils/utils.py
from typing import Optional

def normalizar_profundidad(profundidad) -> Optional[int]:
    """Normaliza el parametro de profundidad"""
    if profundidad is None or profundidad == 'completa':
        return None
    mapa = {'pei': 0, 'objetivos': 1, 'indicadores': 2, 'factores': 2}
    if isinstance(profundidad, str) and profundidad.lower() in mapa:
        return mapa[profundidad.lower()]
    try:
        valor = int(profundidad)
        if 0 <= valor <= 2:
            return valor
    except (ValueError, TypeError):
        pass
    raise ValueError(f"Profundidad inválida: {profundidad}")

def parse_bool_param(valor, default=True) -> bool:
    """Convierte parametro http a Booleano"""
    if valor is None:
        return default
    return str(valor).lower() in ('true', '1', 'si', 'yes')

def generar_filename(tipo_elemento: str, elemento_id: int) -> str:
    """Generar nombre de archivo para descarga"""
    return f"reporte_{tipo_elemento}_{elemento_id}.docx"

def validar_tipo_indicador(tipo: str) -> str:
    """Valida y normaliza el tipo de indicador"""
    tipo = str(tipo).upper()
    return tipo if tipo in ('CUANTITATIVO', 'CUALITATIVO', 'TODOS') else 'TODOS'
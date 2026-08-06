# spme/spme_tree_reporter/services/reporte_proyecto_service.py
"""
ReporteProyectoService: Orquestador principal de generación de reportes.
Coordina repositorio, contexto, walker y renderers.
"""

from io import BytesIO

from ..repositories.arbol_repository import ArbolRepository
from .core.context import ReportContext
from .core.walker import TreeWalker
from .renderers import RendererRegistry
from datetime import date

class ReporteProyectoService:
    """
    Servicio para generar reportes Word concatenados desde cualquier nodo.
    
    Flujo completo:
    1. Obtener árbol jerárquico (vía ArbolRepository)
    2. Crear ReportContext (documento Word vacío + estado)
    3. Crear TreeWalker con RendererRegistry
    4. Recorrer el árbol → cada renderer genera su fragmento
    5. Generar anexo de actividades (si aplica)
    6. Finalizar documento (índice, numeración)
    7. Retornar BytesIO
    
    Uso:
        service = ReporteProyectoService()
        buffer = service.generar_reporte(
            tipo_nodo='proyecto',
            nodo_id=48,
            profundidad='all',
            modo_actividades='anexo'
        )
    """
    
    # Configuraciones predefinidas
    CONFIG_PREDEFINIDA = {
        'completo': {
            'profundidad': 'all',
            'modo_actividades': 'anexo',
            'incluir_portada': True,
            'incluir_indice': True,
        },
        'ejecutivo': {
            'profundidad': 2,
            'modo_actividades': 'omitir',
            'incluir_portada': True,
            'incluir_indice': False,
        },
        'gerencial': {
            'profundidad': 3,
            'modo_actividades': 'referencia',
            'incluir_portada': True,
            'incluir_indice': True,
        },
        'operativo': {
            'profundidad': 'all',
            'modo_actividades': 'referencia',
            'incluir_portada': False,
            'incluir_indice': True,
        },
        'ficha_tecnica': {
            'profundidad': 'self',
            'modo_actividades': 'omitir',
            'incluir_portada': False,
            'incluir_indice': False,
        },
    }
    
    def __init__(self):
        self.arbol_repo = ArbolRepository()
        self.registry = RendererRegistry()
    
    # =====================================================================
    # GENERACIÓN PRINCIPAL
    # =====================================================================
    
    def generar_reporte(self,
                        tipo_nodo: str = 'proyecto',
                        nodo_id: int = None,
                        profundidad='all',
                        modo_actividades: str = 'anexo',
                        incluir_portada: bool = True,
                        incluir_indice: bool = True) -> BytesIO:
        """
        Genera el reporte Word completo.
        
        Args:
            tipo_nodo: Tipo de nodo inicial (default: 'proyecto')
            nodo_id: ID del nodo (requerido)
            profundidad: 'self' | 1 | 2 | 3 | 4 | 'all'
            modo_actividades: 'omitir' | 'referencia' | 'anexo'
            incluir_portada: Si generar portada (solo aplica si es 'proyecto')
            incluir_indice: Si generar índice de contenidos
        
        Returns:
            BytesIO con el documento .docx listo para descargar
        
        Raises:
            ValueError: Si nodo_id es None
        """
        if nodo_id is None:
            raise ValueError("nodo_id es requerido")
        
        # 1. Obtener árbol
        arbol_dict = self.arbol_repo.obtener_arbol(tipo_nodo, nodo_id, profundidad, 'down')
        
        # 2. Armar configuración
        config = {
            'profundidad': profundidad,
            'modo_actividades': modo_actividades,
            'incluir_portada': incluir_portada and tipo_nodo == 'proyecto',
            'incluir_indice': incluir_indice and tipo_nodo == 'proyecto',
        }
        
        # 3. Crear contexto
        context = ReportContext(config)
        
        # 4. Crear walker y recorrer el árbol
        walker = TreeWalker(context, self.registry, self.arbol_repo)
        walker.walk(arbol_dict)
        
        # 5. Generar anexo de actividades (si aplica)
        if modo_actividades == 'anexo':
            walker.generar_anexo_actividades()
        
        # 6. Finalizar documento
        doc = context.finalizar()
        
        # 7. Guardar a buffer
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    # =====================================================================
    # GENERACIÓN POR TIPO PREDEFINIDO
    # =====================================================================
    
    def generar_reporte_predefinido(self, tipo_nodo: str, nodo_id: int, tipo: str = 'completo') -> BytesIO:
        """
        Genera un reporte usando una configuración predefinida.
        
        Args:
            tipo_nodo: Tipo de nodo inicial
            nodo_id: ID del nodo
            tipo: 'completo' | 'ejecutivo' | 'gerencial' | 'operativo' | 'ficha_tecnica'
        
        Returns:
            BytesIO con el documento .docx
        """
        config = self.CONFIG_PREDEFINIDA.get(tipo, self.CONFIG_PREDEFINIDA['completo'])
        
        return self.generar_reporte(
            tipo_nodo=tipo_nodo,
            nodo_id=nodo_id,
            profundidad=config['profundidad'],
            modo_actividades=config['modo_actividades'],
            incluir_portada=config['incluir_portada'],
            incluir_indice=config['incluir_indice'],
        )
    
    # =====================================================================
    # MÉTODOS DE CONVENIENCIA
    # =====================================================================
    
    def reporte_completo(self, proyecto_id: int) -> BytesIO:
        """Reporte completo del proyecto con anexo de actividades."""
        return self.generar_reporte_predefinido('proyecto', proyecto_id, 'completo')
    
    def reporte_ejecutivo(self, proyecto_id: int) -> BytesIO:
        """Reporte ejecutivo (2 niveles, sin actividades)."""
        return self.generar_reporte_predefinido('proyecto', proyecto_id, 'ejecutivo')
    
    def reporte_gerencial(self, proyecto_id: int) -> BytesIO:
        """Reporte gerencial (3 niveles, referencia a actividades)."""
        return self.generar_reporte_predefinido('proyecto', proyecto_id, 'gerencial')
    
    def reporte_operativo(self, proyecto_id: int) -> BytesIO:
        """Reporte operativo (todos los niveles, referencia a actividades)."""
        return self.generar_reporte_predefinido('proyecto', proyecto_id, 'operativo')
    
    def ficha_tecnica(self, proyecto_id: int) -> BytesIO:
        """Solo datos del proyecto, sin hijos."""
        return self.generar_reporte_predefinido('proyecto', proyecto_id, 'ficha_tecnica')
    
    def reporte_desde_nodo(self, tipo_nodo: str, nodo_id: int, profundidad='all') -> BytesIO:
        """
        Genera reporte desde cualquier nodo hacia abajo.
        
        Ejemplos:
            service.reporte_desde_nodo('objetivoespecificoog', 50)
            service.reporte_desde_nodo('actividad', 98)
            service.reporte_desde_nodo('resultadoog', 97, profundidad=2)
        """
        return self.generar_reporte(
            tipo_nodo=tipo_nodo,
            nodo_id=nodo_id,
            profundidad=profundidad,
            modo_actividades='anexo',
            incluir_portada=False,
            incluir_indice=False,
        )
    
    # =====================================================================
    # SALIDAS ALTERNATIVAS
    # =====================================================================
    
    def generar_bytes(self, **kwargs) -> bytes:
        """Retorna los bytes del documento (para S3, email, etc.)."""
        buffer = self.generar_reporte(**kwargs)
        return buffer.getvalue()
    
    def get_filename(self, tipo_nodo: str, nodo_id: int, datos: dict = None) -> str:
        """
        Genera nombre de archivo: CODIGO_TIPO_FECHA.docx
        Ejemplo: PROYTSTPRESS_completo_20260806.docx
        """
        fecha = date.today().strftime('%Y%m%d')
        
        if datos and datos.get('codigo'):
            codigo = datos['codigo']
        else:
            codigo = f"{tipo_nodo}{nodo_id}"
        
        return f"{codigo}_completo_{fecha}.docx"

    def get_filename(self, tipo_nodo: str, nodo_id: int, tipo_reporte: str) -> str:
        """
        Genera nombre de archivo descriptivo.
        
        Formato: CODIGO_TIPOREPORTE_FECHA.docx
        Ejemplo: PROYTSTPRESS_completo_20260806.docx
        """
        from datetime import date
        
        # Obtener código del nodo
        try:
            arbol = self.arbol_repo.obtener_arbol(tipo_nodo, nodo_id, 'self', 'down')
            codigo = arbol.get('datos', {}).get('codigo', f"{tipo_nodo}_{nodo_id}")
        except:
            codigo = f"{tipo_nodo}_{nodo_id}"
        
        fecha = date.today().strftime('%Y%m%d')
        
        return f"{codigo}_{tipo_reporte}_{fecha}.docx"
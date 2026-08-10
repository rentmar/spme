from typing import Optional, Any
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone

from spme_proyectos_reportes.repositories.bitacora_crud_repository import (
    BitacoraCrudRepository
)


class BitacoraCrudService:
    """
    Capa de lógica de negocio para bitácoras de indicadores.
    Orquesta el repositorio, aplica validaciones y reglas de negocio.
    Trata cada modelo como independiente.
    
    Uso:
        repo = BitacoraCrudRepository(BitacoraPrincipalIndicadorOg)
        service = BitacoraCrudService(repo, 'indicador_og_id')
        entrada = service.crear(usuario=..., indicador_id=1, ...)
    """
    
    def __init__(self, repository: BitacoraCrudRepository, campo_indicador: str):
        self.repository = repository
        self.campo_indicador = campo_indicador
    
    # ═══════════════════════════════════════════════════════
    # CREACIÓN
    # ═══════════════════════════════════════════════════════
    
    def crear(
        self,
        usuario_registro,
        indicador_id: int,
        tipo_dato: str,
        valor_literal: Optional[str] = None,
        valor_numerico: Optional[float] = None,
        valor_porcentual: Optional[float] = None,
        fecha_registro: Optional[date] = None,
        observaciones: Optional[str] = None,
        archivos_adjuntos: Optional[dict] = None,
        informe_actividad=None,
        informe_tarea=None,
        snapshot_indicador: Optional[dict] = None,
    ) -> Any:
        """
        Crea una entrada validando consistencia tipo_dato vs valor.
        
        Raises:
            ValidationError: Si los datos no son coherentes
        """
        self._validar_datos(tipo_dato, valor_literal, valor_numerico, valor_porcentual)
        
        datos = {
            self.campo_indicador: indicador_id,
            'tipo_indicador': self._get_tipo_indicador(),
            'tipo_dato': tipo_dato,
            'valor_literal': valor_literal,
            'valor_numerico': valor_numerico,
            'valor_porcentual': valor_porcentual,
            'fecha_registro': fecha_registro or timezone.now().date(),
            'observaciones': observaciones,
            'archivos_adjuntos': archivos_adjuntos or {},
            'usuario_registro': usuario_registro,
            'snapshot_indicador': snapshot_indicador or {},
        }
        
        if informe_actividad:
            datos['informe_actividad'] = informe_actividad
        if informe_tarea:
            datos['informe_tarea'] = informe_tarea
        
        return self.repository.crear(**datos)
    
    def crear_desde_informe_actividad(
        self, usuario_registro, indicador_id: int, informe_actividad,
        tipo_dato: str, **valores
    ):
        """Crea entrada desde un informe de actividad"""
        return self.crear(
            usuario_registro=usuario_registro,
            indicador_id=indicador_id,
            tipo_dato=tipo_dato,
            informe_actividad=informe_actividad,
            **valores
        )
    
    def crear_desde_informe_tarea(
        self, usuario_registro, indicador_id: int, informe_tarea,
        tipo_dato: str, **valores
    ):
        """Crea entrada desde un informe de tarea"""
        return self.crear(
            usuario_registro=usuario_registro,
            indicador_id=indicador_id,
            tipo_dato=tipo_dato,
            informe_tarea=informe_tarea,
            **valores
        )
    
    # ═══════════════════════════════════════════════════════
    # CONSULTA
    # ═══════════════════════════════════════════════════════
    
    def consultar(
        self,
        indicador_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        **filtros_extra
    ):
        """
        Consulta bitácoras con filtros opcionales.
        Ordenado por fecha descendente.
        """
        filtros = dict(filtros_extra)
        
        if indicador_id:
            filtros[self.campo_indicador] = indicador_id
        
        if fecha_inicio and fecha_fin:
            return self.repository.filtrar_por_fechas(fecha_inicio, fecha_fin, **filtros)
        
        return self.repository.filtrar(**filtros).order_by(
            '-fecha_registro', '-timestamp_registro'
        )
    
    def obtener_por_id(self, id: int) -> Optional[Any]:
        """Obtiene un registro por ID"""
        return self.repository.obtener_por_id(id)
    
    def obtener_todos(self):
        """Obtiene todos los registros"""
        return self.repository.obtener_todos()
    
    def obtener_ultimo(self, indicador_id: int):
        """Obtiene el último registro de un indicador"""
        return self.repository.obtener_ultimo(
            **{self.campo_indicador: indicador_id}
        )

    def obtener_por_indicador(self, indicador_id: int):
        """
        Obtiene todas las entradas de un indicador específico.
        Ordenado por fecha descendente.
        """
        return self.repository.filtrar(
            **{self.campo_indicador: indicador_id}
        ).order_by('-fecha_registro', '-timestamp_registro')
    
    # ═══════════════════════════════════════════════════════
    # ACTUALIZACIÓN
    # ═══════════════════════════════════════════════════════
    
    def actualizar(self, id: int, **campos) -> Optional[Any]:
        """
        Actualiza campos de un registro.
        Valida tipo_dato si se incluye en la actualización.
        """
        if 'tipo_dato' in campos:
            self._validar_datos(
                campos.get('tipo_dato'),
                campos.get('valor_literal'),
                campos.get('valor_numerico'),
                campos.get('valor_porcentual')
            )
        return self.repository.actualizar(id, **campos)
    
    # ═══════════════════════════════════════════════════════
    # ELIMINACIÓN
    # ═══════════════════════════════════════════════════════
    
    def eliminar(self, id: int) -> bool:
        """Elimina un registro por ID"""
        return self.repository.eliminar(id)
    
    # ═══════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════
    
    def existe(self, id: int) -> bool:
        """Verifica si existe un registro por ID"""
        return self.repository.existe(id=id)
    
    def contar(self, indicador_id: Optional[int] = None, **filtros) -> int:
        """Cuenta registros, opcionalmente por indicador"""
        if indicador_id:
            filtros[self.campo_indicador] = indicador_id
        return self.repository.contar(**filtros)
    
    # ═══════════════════════════════════════════════════════
    # INTERNOS
    # ═══════════════════════════════════════════════════════
    
    def _validar_datos(
        self,
        tipo_dato: str,
        valor_literal: Optional[str] = None,
        valor_numerico: Optional[float] = None,
        valor_porcentual: Optional[float] = None,
    ):
        """Valida coherencia entre tipo_dato y el valor proporcionado"""
        errores = {}
        
        if tipo_dato == 'A-Z' and not valor_literal:
            errores['valor_literal'] = 'Requerido para tipo de dato A-Z'
        elif tipo_dato == '1-9' and valor_numerico is None:
            errores['valor_numerico'] = 'Requerido para tipo de dato 1-9'
        elif tipo_dato == '%' and valor_porcentual is None:
            errores['valor_porcentual'] = 'Requerido para tipo de dato %'
        
        if errores:
            raise ValidationError(errores)
    
    def _get_tipo_indicador(self) -> str:
        """Determina el tipo_indicador según el campo FK"""
        mapeo = {
            'indicador_og_id': 'indicadorog',
            'indicador_oe_id': 'indicadoroe',
            'indicador_rog_id': 'indicadorrog',
            'indicador_roe_id': 'indicadorroe',
        }
        return mapeo.get(self.campo_indicador, '')
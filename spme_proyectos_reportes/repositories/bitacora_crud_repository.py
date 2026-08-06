from django.db import transaction
from django.db.models import QuerySet
from typing import Optional, Any
from datetime import date


class BitacoraCrudRepository:
    """
    Capa de acceso a datos para bitácoras de indicadores.
    Solo operaciones CRUD. Sin lógica de negocio.
    Trata cada modelo como independiente.
    
    Uso:
        repo = BitacoraCrudRepository(BitacoraPrincipalIndicadorOg)
        entrada = repo.crear(indicador_og=..., tipo_dato='1-9', ...)
    """
    
    def __init__(self, model):
        self.model = model
    
    # ─── CREAR ────────────────────────────────────
    
    def crear(self, **kwargs) -> Any:
        """Crea un registro con soporte transaccional"""
        with transaction.atomic():
            return self.model.objects.create(**kwargs)
    
    # ─── LEER ─────────────────────────────────────
    
    def obtener_por_id(self, id: int) -> Optional[Any]:
        """Obtiene un registro por su ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def obtener_todos(self) -> QuerySet:
        """Obtiene todos los registros"""
        return self.model.objects.all()
    
    def filtrar(self, **filtros) -> QuerySet:
        """Filtra registros por campos específicos"""
        return self.model.objects.filter(**filtros)
    
    def filtrar_por_fechas(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        **filtros_extra
    ) -> QuerySet:
        """
        Filtra registros en rango de fechas.
        Ordenado por fecha_registro descendente y timestamp_registro descendente.
        """
        return self.model.objects.filter(
            fecha_registro__gte=fecha_inicio,
            fecha_registro__lte=fecha_fin,
            **filtros_extra
        ).order_by('-fecha_registro', '-timestamp_registro')
    
    def obtener_ultimo(self, **filtros) -> Optional[Any]:
        """Obtiene el último registro según filtros"""
        return self.model.objects.filter(
            **filtros
        ).order_by('-fecha_registro', '-timestamp_registro').first()
    
    # ─── ACTUALIZAR ───────────────────────────────
    
    def actualizar(self, id: int, **campos) -> Optional[Any]:
        """Actualiza campos de un registro existente"""
        instancia = self.obtener_por_id(id)
        if instancia:
            for campo, valor in campos.items():
                setattr(instancia, campo, valor)
            with transaction.atomic():
                instancia.save()
        return instancia
    
    # ─── ELIMINAR ─────────────────────────────────
    
    def eliminar(self, id: int) -> bool:
        """Elimina un registro por ID"""
        instancia = self.obtener_por_id(id)
        if instancia:
            with transaction.atomic():
                instancia.delete()
            return True
        return False
    
    # ─── UTILIDADES ───────────────────────────────
    
    def existe(self, **filtros) -> bool:
        """Verifica si existe al menos un registro"""
        return self.model.objects.filter(**filtros).exists()
    
    def contar(self, **filtros) -> int:
        """Cuenta registros según filtros"""
        return self.model.objects.filter(**filtros).count()
# spme_proyectos_reportes/services/indicadores/bitacora_og.py

import logging
from datetime import date
from spme_proyectos_reportes.models import BitacoraPrincipalIndicadorOg
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)


class BitacoraOgService:
    """CRUD para BitacoraPrincipalIndicadorOg (Indicador Objetivo General)."""

    @staticmethod
    def crear_actividad(informe_actividad, item_json):
        """
        Crea bitácora OG desde un item del JSON avanceIndicadores.indicadorog.
        
        Args:
            informe_actividad: Instancia de InformeActividadPrincipal.
            item_json (dict): Item del array indicadorog del JSON.
                {
                    "id_indicador": 147,
                    "tipo_dato": "1-9",
                    "valor_numerico": 123,
                    "valor_literal": null,
                    "valor_porcentual": null,
                    "fecha_registro": "2026-05-20",
                    "observaciones": "Obser val num 123",
                    "registrado_por_id": 72,
                    "tipo_indicador": "indicadorog"
                }
        
        Returns:
            BitacoraPrincipalIndicadorOg.
        """
        return BitacoraOgService._crear(informe_actividad, None, item_json)

    @staticmethod
    def crear_tarea(informe_tarea, item_json):
        """Crea bitácora OG desde JSON vinculada a informe de tarea."""
        return BitacoraOgService._crear(None, informe_tarea, item_json)

    @staticmethod
    def actualizar(bitacora_id, validated_data):
        bitacora = BitacoraOgService.obtener_por_id(bitacora_id)
        if not bitacora:
            raise ValueError(f"Bitácora OG con ID {bitacora_id} no encontrada")
        campos = ['tipo_dato', 'valor_literal', 'valor_numerico', 'valor_porcentual', 'fecha_registro', 'observaciones']
        for campo in campos:
            if campo in validated_data:
                setattr(bitacora, campo, validated_data[campo])
        bitacora.save()
        logger.info(f"Bitácora OG actualizada - ID: {bitacora.id}")
        return bitacora

    @staticmethod
    def eliminar(bitacora_id):
        bitacora = BitacoraOgService.obtener_por_id(bitacora_id)
        if not bitacora:
            raise ValueError(f"Bitácora OG con ID {bitacora_id} no encontrada")
        bitacora.delete()
        logger.info(f"Bitácora OG eliminada - ID: {bitacora_id}")
        return True

    @staticmethod
    def obtener_por_id(bitacora_id):
        try:
            return BitacoraPrincipalIndicadorOg.objects.get(id=bitacora_id)
        except BitacoraPrincipalIndicadorOg.DoesNotExist:
            return None

    @staticmethod
    def obtener_por_informe_actividad(informe_actividad_id):
        return BitacoraPrincipalIndicadorOg.objects.filter(informe_actividad_id=informe_actividad_id).order_by('-fecha_registro')

    @staticmethod
    def obtener_por_informe_tarea(informe_tarea_id):
        return BitacoraPrincipalIndicadorOg.objects.filter(informe_tarea_id=informe_tarea_id).order_by('-fecha_registro')

    @staticmethod
    def obtener_por_indicador(indicador_og_id):
        return BitacoraPrincipalIndicadorOg.objects.filter(indicador_og_id=indicador_og_id).order_by('-fecha_registro')

    # ============================================================
    # PRIVADO
    # ============================================================
    @staticmethod
    def _crear(informe_actividad, informe_tarea, item):
        from spme_monitoreo.models import InformeActividadPrincipal, InformeTareaPrincipal

        kwargs = {
            'tipo_indicador': item.get('tipo_indicador', 'indicadorog'),
            'tipo_dato': item.get('tipo_dato'),
            'fecha_registro': item.get('fecha_registro', date.today()),
            'observaciones': item.get('observaciones'),
            'indicador_og_id': item.get('id_indicador'),
        }

        # Valor según tipo_dato
        tipo_dato = item.get('tipo_dato')
        if tipo_dato == 'A-Z':
            kwargs['valor_literal'] = item.get('valor_literal')
        elif tipo_dato == '1-9':
            kwargs['valor_numerico'] = item.get('valor_numerico')
        elif tipo_dato == '%':
            kwargs['valor_porcentual'] = item.get('valor_porcentual')

        # Usuario
        usuario_id = item.get('registrado_por_id')
        if usuario_id:
            try:
                kwargs['usuario_registro'] = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"Usuario {usuario_id} no encontrado")

        # Informe actividad
        if informe_actividad:
            kwargs['informe_actividad'] = informe_actividad
        # Informe tarea
        if informe_tarea:
            kwargs['informe_tarea'] = informe_tarea

        bitacora = BitacoraPrincipalIndicadorOg(**kwargs)
        bitacora.save()
        logger.info(f"Bitácora OG creada - ID: {bitacora.id}, Indicador: {item.get('id_indicador')}")
        return bitacora
# spme_proyectos_reportes/services/indicadores/bitacora_roe.py

import logging
from datetime import date
from spme_proyectos_reportes.models import BitacoraPrincipalIndicadorRoe
from spme_autenticacion.models import Usuario

logger = logging.getLogger(__name__)


class BitacoraRoeService:
    """CRUD para BitacoraPrincipalIndicadorRoe (Indicador Resultado OE)."""

    @staticmethod
    def crear_actividad(informe_actividad, item_json):
        return BitacoraRoeService._crear(informe_actividad, None, item_json)

    @staticmethod
    def crear_tarea(informe_tarea, item_json):
        return BitacoraRoeService._crear(None, informe_tarea, item_json)

    @staticmethod
    def actualizar(bitacora_id, validated_data):
        bitacora = BitacoraRoeService.obtener_por_id(bitacora_id)
        if not bitacora:
            raise ValueError(f"Bitácora ROE con ID {bitacora_id} no encontrada")
        campos = ['tipo_dato', 'valor_literal', 'valor_numerico', 'valor_porcentual', 'fecha_registro', 'observaciones']
        for campo in campos:
            if campo in validated_data:
                setattr(bitacora, campo, validated_data[campo])
        bitacora.save()
        return bitacora

    @staticmethod
    def eliminar(bitacora_id):
        bitacora = BitacoraRoeService.obtener_por_id(bitacora_id)
        if not bitacora:
            raise ValueError(f"Bitácora ROE con ID {bitacora_id} no encontrada")
        bitacora.delete()
        return True

    @staticmethod
    def obtener_por_id(bitacora_id):
        try:
            return BitacoraPrincipalIndicadorRoe.objects.get(id=bitacora_id)
        except BitacoraPrincipalIndicadorRoe.DoesNotExist:
            return None

    @staticmethod
    def obtener_por_informe_actividad(informe_actividad_id):
        return BitacoraPrincipalIndicadorRoe.objects.filter(informe_actividad_id=informe_actividad_id).order_by('-fecha_registro')

    @staticmethod
    def obtener_por_informe_tarea(informe_tarea_id):
        return BitacoraPrincipalIndicadorRoe.objects.filter(informe_tarea_id=informe_tarea_id).order_by('-fecha_registro')

    @staticmethod
    def obtener_por_indicador(indicador_roe_id):
        return BitacoraPrincipalIndicadorRoe.objects.filter(indicador_roe_id=indicador_roe_id).order_by('-fecha_registro')

    @staticmethod
    def _crear(informe_actividad, informe_tarea, item):
        kwargs = {
            'tipo_indicador': item.get('tipo_indicador', 'indicadorroe'),
            'tipo_dato': item.get('tipo_dato'),
            'fecha_registro': item.get('fecha_registro', date.today()),
            'observaciones': item.get('observaciones'),
            'indicador_roe_id': item.get('id_indicador'),
        }
        tipo_dato = item.get('tipo_dato')
        if tipo_dato == 'A-Z':
            kwargs['valor_literal'] = item.get('valor_literal')
        elif tipo_dato == '1-9':
            kwargs['valor_numerico'] = item.get('valor_numerico')
        elif tipo_dato == '%':
            kwargs['valor_porcentual'] = item.get('valor_porcentual')
        usuario_id = item.get('registrado_por_id')
        if usuario_id:
            try:
                kwargs['usuario_registro'] = Usuario.objects.get(id=int(usuario_id))
            except Usuario.DoesNotExist:
                logger.warning(f"Usuario {usuario_id} no encontrado")
        if informe_actividad:
            kwargs['informe_actividad'] = informe_actividad
        if informe_tarea:
            kwargs['informe_tarea'] = informe_tarea
        bitacora = BitacoraPrincipalIndicadorRoe(**kwargs)
        bitacora.save()
        logger.info(f"Bitácora ROE creada - ID: {bitacora.id}")
        return bitacora
from spme_actividades.models import Actividad


def actualizar_actividades(datos_validados):
    """
    Actualiza actividades existentes.
    Levanta excepción si alguna no existe → rollback.
    """
    for item in datos_validados:
        try:
            actividad = Actividad.objects.get(id=item['id'])
        except Actividad.DoesNotExist:
            raise Exception(f"Actividad con ID {item['id']} no encontrada")

        for campo in [
            'codigo', 'nombreCorto', 'descripcion', 'estado',
            'supuestos', 'riesgos', 'objetivo_de_actividad',
            'descripcion_evaluacion', 'descripcion_tipo_actividad',
            'gradoEjecucion',
        ]:
            if campo in item:
                setattr(actividad, campo, item[campo])

        for campo in ['fecha_programada', 'fecha_inicio', 'fecha_cierre']:
            if campo in item:
                setattr(actividad, campo, item[campo])

        for campo in [
            'presupuesto', 'presupuestoGlobal', 'totalReportado',
            'totalEjecutado', 'saldo',
        ]:
            if campo in item:
                setattr(actividad, campo, item[campo])

        for campo in [
            'procedencia_fondos', 'rutaTrazadoIndicadores',
            'factoresCriticos', 'estructuraProcedencia',
        ]:
            if campo in item:
                setattr(actividad, campo, item[campo])

        for campo in [
            'tipo_id', 'responsable_id', 'proceso_id',
            'resultado_og_id', 'resultado_oe_id', 'producto_oe_id',
            'objetivo_pei_id', 'indicador_pei_id', 'proyecto_id',
        ]:
            if campo in item:
                setattr(actividad, campo, item[campo])

        if 'estaInactiva' in item:
            actividad.estaInactiva = item['estaInactiva']

        actividad.save()


def crear_actividades(datos_validados, proyecto_id):
    """
    Crea nuevas actividades.
    Retorna lista de {id_temporal, id_real} para el resumen.
    """
    mapeo_ids = []

    for item in datos_validados:
        id_temporal = item.get('id')  # ID temporal del frontend

        actividad = Actividad.objects.create(
            proyecto_id=proyecto_id,
            codigo=item.get('codigo'),
            nombreCorto=item.get('nombreCorto', ''),
            descripcion=item.get('descripcion', ''),
            estado=item.get('estado', 'CRD'),
            supuestos=item.get('supuestos', ''),
            riesgos=item.get('riesgos', ''),
            objetivo_de_actividad=item.get('objetivo_de_actividad', ''),
            descripcion_evaluacion=item.get('descripcion_evaluacion', ''),
            descripcion_tipo_actividad=item.get('descripcion_tipo_actividad', ''),
            gradoEjecucion=item.get('gradoEjecucion', 'PLANIFICADA'),
            tipo_id=item.get('tipo_id'),
            responsable_id=item.get('responsable_id'),
            proceso_id=item.get('proceso_id'),
            resultado_og_id=item.get('resultado_og_id'),
            resultado_oe_id=item.get('resultado_oe_id'),
            producto_oe_id=item.get('producto_oe_id'),
            objetivo_pei_id=item.get('objetivo_pei_id'),
            indicador_pei_id=item.get('indicador_pei_id'),
            fecha_programada=item.get('fecha_programada'),
            fecha_inicio=item.get('fecha_inicio'),
            fecha_cierre=item.get('fecha_cierre'),
            presupuesto=item.get('presupuesto', 0),
            presupuestoGlobal=item.get('presupuestoGlobal'),
            totalReportado=item.get('totalReportado'),
            totalEjecutado=item.get('totalEjecutado'),
            saldo=item.get('saldo', 0),
            procedencia_fondos=item.get('procedencia_fondos', []),
            rutaTrazadoIndicadores=item.get('rutaTrazadoIndicadores'),
            factoresCriticos=item.get('factoresCriticos'),
            estructuraProcedencia=item.get('estructuraProcedencia'),
            estaInactiva=item.get('estaInactiva', False),
        )

        if id_temporal:
            mapeo_ids.append({
                'id_temporal': id_temporal,
                'id_real': actividad.id,
            })

    return mapeo_ids
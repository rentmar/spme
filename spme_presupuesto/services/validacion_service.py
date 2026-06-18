#spme/spme_presupuesto/services/validacion_service.py

class ValidacionService:
    """
    Validaciones de consistencia en la planificación presupuestaria
    """

    @staticmethod
    def validar_procedencia_fondos_actividad(actividad):
        if not actividad.procedencia_fondos:
            return True, "La actividad no tiene desglose de fuentes.", 0, []

        if not isinstance(actividad.procedencia_fondos, list):
            return False, "El campo procedencia_fondos debe ser una lista.", 0, []
        
        detalle = []
        suma_fuentes = 0

        for f in actividad.procedencia_fondos:
            nombre = f.get('nombre', 'Desconocido')
            monto = float(f.get('monto', 0))
            detalle.append({'nombre': nombre, 'monto': monto})
            suma_fuentes += monto
        
        presupuesto = float(actividad.presupuesto or 0)

        if abs(suma_fuentes - presupuesto) > 0.01:
            return False, (
                f"La suma de fuentes (${suma_fuentes:,.2f}) no coincide "
                f"con el presupuesto de la actividad (${presupuesto:,.2f}). "
                f"Diferencia: ${abs(suma_fuentes - presupuesto):,.2f}"
            ), suma_fuentes, detalle
        
        return True, "La suma de fuentes coincide con el presupuesto de la actividad.", suma_fuentes, detalle

    @staticmethod
    def validar_presupuesto_global(proyecto):
        from spme_presupuesto.repositories.planificacion_repository import PlanificacionRepository

        actividades = PlanificacionRepository.obtener_actividad_planificadas(proyecto.id)
        suma_actividades = sum(float(a.presupuesto or 0) for a in actividades)
        presupuesto = float(proyecto.presupuesto or 0)

        detalle = [
            {
                'codigo': a.codigo or '',
                'nombre': a.nombreCorto or '',
                'presupuesto': float(a.presupuesto or 0),
            }
            for a in actividades
        ]

        if suma_actividades == 0:
            return True, "No hay actividades con presupuesto registrado.", 0, detalle

        if abs(suma_actividades - presupuesto) > 0.01:
            return False, (
                f"La suma de actividades (${suma_actividades:,.2f}) no coincide "
                f"con el presupuesto del proyecto (${presupuesto:,.2f}). "
                f"Diferencia: ${abs(suma_actividades - presupuesto):,.2f}"
            ), suma_actividades, detalle

        return True, "El presupuesto del proyecto coincide con la suma de actividades.", suma_actividades, detalle
    
    @staticmethod
    def validar_partidas_tarea(tarea):
        if not tarea.presupuestoDesglose:
            return True, "La tarea no tiene partidas registradas.", 0

        if not isinstance(tarea.presupuestoDesglose, list):
            return False, "El campo presupuestoDesglose debe ser una lista.", 0
        
        suma_partidas = sum(float(p.get('monto', 0)) for p in tarea.presupuestoDesglose)
        presupuesto = float(tarea.presupuesto or 0)

        if abs(suma_partidas - presupuesto) > 0.01:
            return False, (
                f"La suma de partidas (${suma_partidas:,.2f}) no coincide "
                f"con el presupuesto de la tarea (${presupuesto:,.2f}). "
                f"Diferencia: ${abs(suma_partidas - presupuesto):,.2f}"
            ), suma_partidas
        
        return True, "La suma de partidas coincide con el presupuesto de la tarea.", suma_partidas
        

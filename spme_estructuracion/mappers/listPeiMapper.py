
class ListPeiMapper:
    @staticmethod

    def toListPeiResponse(qsPei):
        listaPei = []
        for reg in qsPei:
            listaPei.append({
                "id": reg.id,
                "titulo": reg.titulo,
                "descripcion": reg.descripcion,
                "fecha_creacion": reg.fecha_creacion,
                "fecha_inicio": reg.fecha_inicio,
                "fecha_fin": reg.fecha_fin,
                "esta_vigente": reg.esta_vigente,
                "creado_el": reg.creado_el.isoformat() if reg.creado_el else None,
                "modificado_el": reg.modificado_el.isoformat() if reg.modificado_el else None
            }
        )
        # Retorna la lista de PEI en el formato esperado
        return {
            "lista_pei": listaPei
        }
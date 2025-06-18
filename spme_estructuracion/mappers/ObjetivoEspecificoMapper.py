class ObjetivoEspecificoMapper:
    @staticmethod
    def toObjetivoEspecificoResponse(lista):
        objetivo_estecifico_lista = []
        for item in lista:
           
            objetivo_estecifico_lista.append(
            {
                "id": item.id,
                "codigo": item.codigo,
                "descripcion": item.descripcion,
                "supuestos": item.supuestos,
                "riesgos": item.riesgos,
                "proyecto_id": item.proyecto_id
            })
            
        return {
             "objetivo_especifico_lista":objetivo_estecifico_lista
            }
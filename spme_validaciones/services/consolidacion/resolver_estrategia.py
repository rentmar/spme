# spme/spme_validaciones/services/consolidacion/resolver_estrategia.py
from .modelos import MetodoResolucion
from .estrategias.todo_o_nada import EstrategiaTodoONada
from .estrategias.decisorio import EstrategiaDecisorio

class MetodoResolucionNoSoportado(Exception):
    pass


class ResolverEstrategia:
    def resolver(self, metodo_resolucion: str):

        if metodo_resolucion == MetodoResolucion.TODO_O_NADA:
            return EstrategiaTodoONada()

        if metodo_resolucion == MetodoResolucion.DECISORIO:
            return EstrategiaDecisorio()

        raise MetodoResolucionNoSoportado(
            f"Método de resolución no soportado: "
            f"{metodo_resolucion}"
        )

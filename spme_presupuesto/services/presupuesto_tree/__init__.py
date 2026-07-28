from .registry import PresupuestoRegistry
from .orchestrator import PresupuestoOrchestrator
from .builders.proyecto_builder import ProyectoPresupuestoBuilder
from .builders.actividad_builder import ActividadPresupuestoBuilder
from .builders.tarea_builder import TareaPresupuestoBuilder
from .builders.resultado_actividades_builder import ResultadoActividadesBuilder
from .builders.resultado_tareas_builder import ResultadoTareasBuilder

registry = PresupuestoRegistry()
registry.register_builder('proyecto', ProyectoPresupuestoBuilder())
registry.register_builder('actividad', ActividadPresupuestoBuilder())
registry.register_builder('tarea', TareaPresupuestoBuilder())
registry.register_builder('resultado_actividades', ResultadoActividadesBuilder())
registry.register_builder('resultado_tareas', ResultadoTareasBuilder())

presupuesto_orchestrator = PresupuestoOrchestrator(registry)
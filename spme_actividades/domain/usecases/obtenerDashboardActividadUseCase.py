from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer
from spme_estructuracion_pei.container.repositoryContainer import EstructuracionPeiRepositoryContainer
from spme_estructuracion_proyecto.container.repositoryContainer import ProyectoRepositoryContainer

class ObtenerDashboardActividadUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()
        self.PeiContenedor = EstructuracionPeiRepositoryContainer()
        self.estructuracionPeiRepository = self.PeiContenedor.estructuracionPeiRepository()
        self.proyectoContenedor = ProyectoRepositoryContainer()
        self.proyectoRepository = self.proyectoContenedor.proyectoRepository()

    def execute(self):
        
        datosResponse = {} 

        numeroTotalActividades = self.actividadesRepository.numeroTotalActividades()

        if numeroTotalActividades is None:
            datosResponse["numero_total_actividades"] = 0
        else:
            datosResponse["numero_total_actividades"] = numeroTotalActividades

        actividadesPlanificadas = self.actividadesRepository.totalActividadesPlanificadas()

        if actividadesPlanificadas is None:
            datosResponse["numero_actividades_planificadas"] = 0
        else:
            datosResponse["numero_actividades_planificadas"] = actividadesPlanificadas

        actividadesEjecucion = self.actividadesRepository.totalActividadesEnEjecucion()

        if actividadesEjecucion is None:
            datosResponse["numero_actividades_ejecucion"] = 0
        else:
            datosResponse["numero_actividades_ejecucion"] = actividadesEjecucion

        actividadesFin = self.actividadesRepository.totalActividadesFinalizadas()

        if actividadesFin is None:
            datosResponse["numero_actividades_finalizadas"] = 0
        else:
            datosResponse["numero_actividades_finalizadas"] = actividadesFin

        sumaPresupuestos = self.actividadesRepository.sumaPresupuestos()

        if sumaPresupuestos is None:
            datosResponse["suma_presupuestos"]=0
        else:
            datosResponse["suma_presupuestos"]=sumaPresupuestos

        sumaPresupuestosGlobales = self.actividadesRepository.sumaPresupuestosGlobales()

        if sumaPresupuestos is None:
            datosResponse["suma_presupuestos_globales"]=0
        else:
            datosResponse["suma_presupuestos_globales"]=sumaPresupuestosGlobales

        numPeiVigentes = self.estructuracionPeiRepository.numeroPeiVigente()

        if numPeiVigentes is None:
            datosResponse["numero_pei_vigentes"]=0
        else:
            datosResponse["numero_pei_vigentes"]=numPeiVigentes

        numPeiTotal = self.estructuracionPeiRepository.numeroTotalPei()

        if numPeiTotal is None:
            datosResponse["numero_total_pei"]=0
        else:
            datosResponse["numero_total_pei"]=numPeiTotal

        numProyectos = self.proyectoRepository.numeroProyectos()

        if numProyectos is None:
            datosResponse["numero_total_proyectos"]=0
        else:
            datosResponse["numero_total_proyectos"]=numProyectos
      
        return datosResponse       
from spme_actividades.container.repositoryContainer import ActividadesRepositoryContainer

class ObtenerDashboardActividadUseCase:
    def __init__(self):
        self.contenedor = ActividadesRepositoryContainer()
        self.actividadesRepository = self.contenedor.actividadesRepository()

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
      
        return datosResponse       
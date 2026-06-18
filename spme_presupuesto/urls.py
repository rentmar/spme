from django.urls import path, include
from rest_framework.routers import DefaultRouter
from spme_presupuesto.views.consulta_views import EstadoPresupuestoProyectoView
from .views.planificacion_views import (
    ProyectoPlanificacionView,
    ActividadesPlanificadasView,
    TareasPlanificadasView,
    ConsolidadoFuentesView,
    ValidarActividadView,
    ValidarProyectoView,
    ValidarTareaView,
)

router = DefaultRouter()

urlpatterns = [
    #Consulta de permisos
    path(r'estado/<int:proyecto_id>/', EstadoPresupuestoProyectoView.as_view(), name='estado_presupuesto' ),
    ############################# Planificación ###############################
    path(r'planificacion/proyecto/<int:proyecto_id>/', ProyectoPlanificacionView.as_view(), name='planificacion_proyecto'),
    path(r'planificacion/actividades/<int:proyecto_id>/', ActividadesPlanificadasView.as_view(), name='planificacion_actividades'),
    path(r'planificacion/tareas/<int:actividad_id>/', TareasPlanificadasView.as_view(), name='planificacion_tareas'),
    path(r'planificacion/fuentes/<int:proyecto_id>/', ConsolidadoFuentesView.as_view(), name='planificacion_fuentes'),
    ############################# Validacion ###############################
    path(r'validar/actividad/<int:actividad_id>/', ValidarActividadView.as_view(), name='validar_actividad'),
    path(r'validar/proyecto/<int:proyecto_id>/', ValidarProyectoView.as_view(), name='validar_proyecto'),
    path(r'validar/tarea/<int:tarea_id>/', ValidarTareaView.as_view(),name='validar_tarea'),



]

urlpatterns += router.urls
from django.urls import path, include
#from .views import *
from rest_framework.routers import DefaultRouter
from .views.planificacion_proyecto_views import PlanificacionProyectoViewSet
from .views.cambio_planificacion_proyecto_view import CambioPlanificacionProyectoViewSet
from .views.planificacion_idproyecto_views import PlanificacionesPorProyectoAPIView
from .views.cambio_plan_idplan_views import CambiosPlanificacionListView


router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'revisiones', PlanRevisionViewSet, basename='plan-revision')
router.register(r'planificacion-proyecto-respaldo', PlanificacionProyectoViewSet, basename='planificacion_proyecto_respaldo')
router.register(r'cambio-planificacion-proyecto-respaldo', CambioPlanificacionProyectoViewSet, basename='cambio_planificacion_proyecto_respaldo')

urlpatterns = [
    #path(r'planes/<int:plan_id>/crear-revision/', ProyectoPlanViewSet.as_view({'post': 'create_revision'}), name='plan-crear-revision'), 
    #path(r'proyectos/<int:proyectoId>/planificacion/', LatestProjectPlanAPIView.as_view(), name='proyecto-planificacion-ultimo'),
    #Todas las planificaciones de un proyecto mas sus cambios
    path(r'planificaciones/proyecto/<int:proyecto_id>/', PlanificacionesPorProyectoAPIView.as_view(), name='planificacion-por-proyecto' ),
    #Cambios de una planificacion por id de planificacion
    path(r'planificaciones/<int:planificacion_id>/cambios/', CambiosPlanificacionListView.as_view() , name='planificacion-por-proyecto' ),
]

urlpatterns += router.urls


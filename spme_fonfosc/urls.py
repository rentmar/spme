from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views.fonfosc_crud_basico_views import ProyectoFonFoscViews
# from .views.institucion_crud_basico_views import InstitucionViews
# from .views.estructura_fonfosc_views import ProyectoFonFoscViewSet
# from .views.departamentos_bol_crud_basico_viewss import DepBoliviaViews

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
#router.register(r'revisiones', PlanRevisionViewSet, basename='plan-revision')
# router.register(r'fon-fosc-proyectos', ProyectoFonFoscViews, basename='plan-revision')
# router.register(r'instituciones', InstitucionViews, basename='instituciones')
# router.register(r'departamentos-bolivia', DepBoliviaViews, basename='departamentos-bolivia')

urlpatterns = [
    #path(r'planes/<int:plan_id>/crear-revision/', ProyectoPlanViewSet.as_view({'post': 'create_revision'}), name='plan-crear-revision'), 
    #path(r'proyectos/<int:proyectoId>/planificacion/', LatestProjectPlanAPIView.as_view(), name='proyecto-planificacion-ultimo'),
    # path(r'proyectos-fonfosc/<int:pk>/estructura/',  ProyectoFonFoscViewSet.as_view({'get': 'estructura_completa'}),  name='proyecto-fonfosc-estructura'),
]

urlpatterns += router.urls


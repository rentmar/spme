from django.urls import path, include
from rest_framework.routers import DefaultRouter

from spme_fonfosc.views.institucion_crud_basico_views import (
    InstitucionListView,
    InstitucionDetailView,
)

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
    #Instituciones
    path(r'instituciones/', InstitucionListView.as_view(), name='institucion-list'),
    path(r'instituciones/<int:institucion_id>/', InstitucionDetailView.as_view(), name='institucion-detail'),

]

urlpatterns += router.urls


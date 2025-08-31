from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')
router.register(r'revisiones', PlanRevisionViewSet, basename='plan-revision')

urlpatterns = [
    path(r'planes/<int:plan_id>/crear-revision/', ProyectoPlanViewSet.as_view({'post': 'create_revision'}), name='plan-crear-revision'), 
    path(r'proyectos/<int:proyectoId>/planificacion/', LatestProjectPlanAPIView.as_view(), name='proyecto-planificacion-ultimo'),

]

urlpatterns += router.urls


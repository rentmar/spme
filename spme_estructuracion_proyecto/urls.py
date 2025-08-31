from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.proyecto_detalle_views import test_connection, ProyectoDetailView

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')

urlpatterns = [
    path(r'proyectos/test-conexion/', test_connection, name='proyecto-test'),
    path(r'proyectos/<int:id>/detalles/', ProyectoDetailView.as_view(), name='proyecto_detalles_por_id' )

]

urlpatterns += router.urls
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.actualizar_estructura_views import actualizar_estructura_transaccional

router = DefaultRouter()

#router.register(r'planes', ProyectoPlanViewSet, basename='proyecto-plan')

urlpatterns = [
    #path(r'actualizar-estructura/', actualizar_estructura_completa, name='actualizar_estructura'),
    path(r'actualizar-estructura-transaccional/', actualizar_estructura_transaccional, name='actualizar_estructura_transaccional' )

]

urlpatterns += router.urls
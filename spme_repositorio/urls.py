# spme/spme_validaciones/urls.py
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.tree_view import arbol_endpoint

router = DefaultRouter()

#Validadores Informes Actividad/Tarea
#router.register(r'validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    ################################# Validacion de Informes ###################################################
    #Validadores Informes Actividad/Tarea
    #path(r'asignar-validadores/', AsignarValidadoresViewSet.as_view({'post': 'create'}), name='asignar-validadores'),
    path(r'repositorio/arbol/', arbol_endpoint, name='arbol-repositorio'),

]  

urlpatterns += router.urls
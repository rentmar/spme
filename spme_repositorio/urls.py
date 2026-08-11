# spme/spme_validaciones/urls.py
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .views.tree_view import arbol_endpoint
from .views.upload_views import (
    UploadArchivoView, 
    AdjuntosObjetoView,
    EliminarAdjuntoView,
)
from .views.download_views import (
    DescargarArchivoView,
)
#Referencias externas
from .views.referencia_views import (
    ReferenciaListView,
    ReferenciaSingleView,
    ReferenciaBulkView,
    ReferenciaDeleteView,
)

router = DefaultRouter()

#Validadores Informes Actividad/Tarea
#router.register(r'validaciones', ValidacionViewSet, basename='validacion')

urlpatterns = [
    ################################# Validacion de Informes ###################################################
    #Validadores Informes Actividad/Tarea
    #path(r'asignar-validadores/', AsignarValidadoresViewSet.as_view({'post': 'create'}), name='asignar-validadores'),
    path(r'repositorio/arbol/', arbol_endpoint, name='arbol-repositorio'),
    ################################# Repositorio: Adjuntos + Garage #########################
    #Upload al repositorio Garaga
    path(r'repositorio/upload/', UploadArchivoView.as_view(), name='upload-archivo'),
    #Lista los archivos asociados al modelo/nodo(tipo_objeto) y su id
    path(r'repositorio/adjuntos/<str:tipo_objeto>/<int:objeto_id>/', AdjuntosObjetoView.as_view(), name='adjuntos_objetos'),
    #Descarga el archivo almacenado en el bucket por su id
    path(r'repositorio/descargar/<int:archivo_id>/', DescargarArchivoView.as_view(), name='descargar-archivo'),
    #Eliminar adjuntos
    path(r'repositorio/adjuntos/<int:adjunto_id>/', EliminarAdjuntoView.as_view(), name='eliminar-adjunto'),
    ############################### Repositorio: Referencias externas ###########################
    path(r'referencias/<str:tipo_objeto>/<int:objeto_id>/', ReferenciaListView.as_view(), name='referencias-list'),
    path(r'referencias/', ReferenciaSingleView.as_view(), name='referencia-create'),
    path(r'referencias/bulk/', ReferenciaBulkView.as_view(), name='referencia-bulk'),
    path(r'referencias/<int:referencia_id>/', ReferenciaDeleteView.as_view(), name='referencia-delete'),
]  

urlpatterns += router.urls
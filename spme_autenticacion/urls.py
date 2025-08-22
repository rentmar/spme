from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerUsuario/',views.ObtenerUsuario.as_view(), name='obtenerUsuario'),
    path(r'crearUsuario/',views.CrearUsuario.as_view(), name='crearUsuario'),
    path(r'autenticarUsuario/',views.AutenticacionUsuario.as_view(), name='autenticarUsuario'),
    path(r'listaUsuarios/',views.ListaUsuarios.as_view(), name='listaUsuarios'),
    path(r'listaValidadores/',views.ListaValidadores.as_view(), name='listaValidadores'),
]
urlpatterns += router.urls
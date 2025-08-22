from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerActividadesUsuario/',views.ObtenerActividadesUsuario.as_view(), name='obtenerActividadesUsuario'),
    path(r'obtenerActividadesKant/',views.ObtenerActividadesKant.as_view(), name='obtenerActividadesKant'),
    path(r'crearActividad/',views.CrearActividad.as_view(), name='crearActividad'),
    path(r'obtenerActividadId/',views.ObtenerActividadId.as_view(), name='obtenerActividadId'),
    path(r'obtenerEncabezadoActividadId/',views.ObtenerEncabezadoActividad.as_view(), name='obtenerEncabezadoActividadId'),
]
urlpatterns += router.urls


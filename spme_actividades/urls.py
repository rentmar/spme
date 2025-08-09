from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerActividadesUsuario/',views.ObtenerActividadesUsuario.as_view(), name='obtenerActividadesUsuario'),
    path(r'obtenerActividadesKant/',views.ObtenerActividadesKant.as_view(), name='obtenerActividadesKant'),
    path(r'crearActividad/',views.CrearActividad.as_view(), name='crearActividad'),
    path(r'tareas/', views.Tareas.as_view(), name='tareas-actividad')
]
urlpatterns += router.urls


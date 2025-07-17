from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'crearSolicitudFondos/',views.SolicitudFondos.as_view(), name='crearSolicitudFondos'),
    #path(r'obtenerSolicitudFondos/',views.ObtenerSolicitudFondos.as_view(), name='obtenerSolicitudFondos'),
]
urlpatterns += router.urls
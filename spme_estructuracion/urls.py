from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObtenerPei, ObtenerObjetivoEspecifico

# Crear el router y registrar el viewset
router = DefaultRouter()

# Incluir las rutas generadas automáticamente
urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerPei/', ObtenerPei.as_view() , name='obtenerPei'),
    path(r'objetivoEspecifico/', ObtenerObjetivoEspecifico.as_view(), name='objetivoEspecifico'),
]
urlpatterns += router.urls
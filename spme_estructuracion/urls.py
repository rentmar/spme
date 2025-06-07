from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObtenerPei

# Crear el router y registrar el viewset
router = DefaultRouter()

# Incluir las rutas generadas automáticamente
urlpatterns = [
    path('', include(router.urls)),
    path(r'obtenerPei/', ObtenerPei.as_view() , name='obtenerPei'),
]

urlpatterns += router.urls

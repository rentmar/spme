"""
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tareas', views.TareaViewSet, basename='tareas')

urlpatterns = router.urls
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import getLibro

# Crear el router y registrar el viewset
router = DefaultRouter()

# Incluir las rutas generadas automáticamente
urlpatterns = [
    path('', include(router.urls)),
    path(r'libro/', getLibro.as_view() , name='libro'),
]

urlpatterns += router.urls

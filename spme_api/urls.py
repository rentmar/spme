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
from .views import TareaViewSet

# Crear el router y registrar el viewset
router = DefaultRouter()
router.register(r'tareas', TareaViewSet, basename='tareas')

# Incluir las rutas generadas automáticamente
urlpatterns = [
    path('', include(router.urls)),
]
